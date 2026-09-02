"""Deterministic shared-cash paper execution for closed Hixton bars."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import ROUND_DOWN, Decimal

from hixton.backtest.models import BASELINE_COSTS, ONE, ZERO, ExecutionRules
from hixton.constants import HIXTON_SPEC_VERSION, SYMBOLS
from hixton.domain.models import IndicatorPoint, Signal
from hixton.domain.risk import PortfolioRiskState, evaluate_portfolio_risk
from hixton.domain.strategy import HixtonStrategy
from hixton.domain.versions import StrategyDefinition
from hixton.paper.models import (
    PaperAccount,
    PaperEvent,
    PaperEventStatus,
    PaperPortfolio,
    PaperPosition,
)
from hixton.paper.storage import PaperStore

_HUNDRED = Decimal("100")
_ENTRY_LATENCY = timedelta(milliseconds=250)


def _d(value: float) -> Decimal:
    return Decimal(str(value))


def _round_down(value: Decimal, step: Decimal) -> Decimal:
    if step <= ZERO:
        return value
    return (value / step).to_integral_value(rounding=ROUND_DOWN) * step


def _event_id(signal: Signal) -> str:
    return hashlib.sha256(f"PAPER|{signal.signal_id}".encode()).hexdigest()


def initialize_paper_at_latest(
    database_path: str,
    points_by_symbol: Mapping[str, tuple[IndicatorPoint, ...]],
    *,
    at: datetime | None = None,
    strategy_key: str = "v1",
    strategy_version: str = HIXTON_SPEC_VERSION,
) -> bool:
    """Arm a new account at latest; preserve checkpoints on every later restart."""

    if set(points_by_symbol) != set(SYMBOLS):
        raise ValueError("paper initialization requires all ten DMS symbols")
    checkpoints: dict[str, datetime] = {}
    for symbol in SYMBOLS:
        points = points_by_symbol[symbol]
        if not points:
            raise ValueError(f"cannot initialize paper without candles for {symbol}")
        checkpoints[symbol] = points[-1].candle.close_time_utc
    with PaperStore(database_path) as store:
        store.initialize(
            at=at,
            strategy_key=strategy_key,
            strategy_version=strategy_version,
        )
        store.require_strategy(strategy_key, strategy_version)
        existing = store.all_checkpoints()
        if existing and set(existing) != set(SYMBOLS):
            raise RuntimeError("paper checkpoints are incomplete; recovery must fail closed")
        first_start = not existing
        if first_start:
            store.save_checkpoints(checkpoints)
            existing = checkpoints
        store.ensure_soak_started(existing, at=at)
    return first_start


def _signal(point: IndicatorPoint, *, is_long: bool) -> Signal | None:
    return HixtonStrategy.signal_for(point, is_long=is_long)


def _blocked_event(signal: Signal, reason: str) -> PaperEvent:
    return PaperEvent(
        event_id=_event_id(signal),
        signal_id=signal.signal_id,
        occurred_at_utc=signal.candle_close_time_utc,
        symbol=signal.symbol,
        action=signal.action.value,
        status=PaperEventStatus.BLOCKED,
        reason=reason,
        reference_price=_d(signal.close),
        execution_price=None,
        base_quantity=None,
        quote_amount_usdt=None,
        fee_usdt=None,
        realized_pnl_usdt=None,
        breakout_strength=(
            _d(signal.breakout_strength) if signal.breakout_strength is not None else None
        ),
        strategy_version=signal.strategy_version,
    )


def _equity(
    cash: Decimal,
    positions: Mapping[str, PaperPosition],
    latest_prices: Mapping[str, Decimal],
) -> tuple[Decimal, Decimal]:
    market_value = sum(
        (
            position.quantity * latest_prices.get(symbol, position.average_price)
            for symbol, position in positions.items()
        ),
        ZERO,
    )
    basis = sum((position.cost_basis_usdt for position in positions.values()), ZERO)
    return cash + market_value, market_value - basis


def _risk_account(
    account: PaperAccount,
    *,
    equity: Decimal,
    at: datetime,
) -> tuple[PaperAccount, bool, Decimal]:
    decision = evaluate_portfolio_risk(
        PortfolioRiskState(
            high_water_equity_usdt=account.high_water_equity_usdt,
            day_start_equity_usdt=account.day_start_equity_usdt,
            day_start_date_utc=account.day_start_date_utc,
            halted=account.halted,
            halt_reason=account.halt_reason,
        ),
        equity=equity,
        at=at,
    )
    updated = replace(
        account,
        high_water_equity_usdt=decision.state.high_water_equity_usdt,
        day_start_equity_usdt=decision.state.day_start_equity_usdt,
        day_start_date_utc=decision.state.day_start_date_utc,
        halted=decision.state.halted,
        halt_reason=decision.state.halt_reason,
        updated_at_utc=at.astimezone(UTC),
    )
    return updated, decision.daily_paused, decision.drawdown_pct


def process_new_closed_points(
    database_path: str,
    points_by_symbol: Mapping[str, tuple[IndicatorPoint, ...]],
    rules_by_symbol: Mapping[str, ExecutionRules],
    *,
    strategy_key: str = "v1",
    strategy_version: str = HIXTON_SPEC_VERSION,
) -> tuple[PaperEvent, ...]:
    """Process every not-yet-checkpointed bar atomically and exactly once."""

    if set(points_by_symbol) != set(SYMBOLS):
        raise ValueError("paper processing requires all ten DMS symbols")
    if set(rules_by_symbol) != set(SYMBOLS):
        raise ValueError("paper processing requires exchange rules for all symbols")

    with PaperStore(database_path) as store:
        store.initialize(
            strategy_key=strategy_key,
            strategy_version=strategy_version,
        )
        store.require_strategy(strategy_key, strategy_version)
        account = store.load_account()
        settings = store.load_settings()
        positions = {position.symbol: position for position in store.load_positions()}
        checkpoints = store.all_checkpoints()
        if set(checkpoints) != set(SYMBOLS):
            raise RuntimeError("paper checkpoints are incomplete; run startup initialization")
        store.ensure_soak_started(checkpoints)

        pending: dict[datetime, list[IndicatorPoint]] = {}
        processed_bars = dict.fromkeys(SYMBOLS, 0)
        latest_prices: dict[str, Decimal] = {}
        for symbol in SYMBOLS:
            for point in points_by_symbol[symbol]:
                latest_prices[symbol] = _d(point.candle.close)
                if point.candle.close_time_utc > checkpoints[symbol]:
                    pending.setdefault(point.candle.close_time_utc, []).append(point)

        emitted: list[PaperEvent] = []
        for close_time, group in sorted(pending.items()):
            group_by_symbol = {point.symbol: point for point in group}
            for symbol, point in group_by_symbol.items():
                latest_prices[symbol] = _d(point.candle.close)
                processed_bars[symbol] += 1

            equity, _ = _equity(account.cash_usdt, positions, latest_prices)
            account, daily_paused, _ = _risk_account(account, equity=equity, at=close_time)

            for point in group:
                if not point.flip_down or point.symbol not in positions:
                    continue
                signal = _signal(point, is_long=True)
                if signal is None:
                    continue
                position = positions[point.symbol]
                rules = rules_by_symbol[point.symbol]
                reference = _d(signal.close)
                fill_price = reference * (ONE - BASELINE_COSTS.adverse_price_rate)
                quantity = _round_down(position.quantity, rules.step_size)
                gross_quote = quantity * fill_price
                if quantity < rules.min_qty or gross_quote < rules.min_notional:
                    emitted.append(_blocked_event(signal, "EXIT_BECAME_DUST"))
                    del positions[point.symbol]
                    continue
                fee = gross_quote * BASELINE_COSTS.fee_rate
                net_quote = gross_quote - fee
                account = replace(account, cash_usdt=account.cash_usdt + net_quote)
                realized = net_quote - position.cost_basis_usdt
                emitted.append(
                    PaperEvent(
                        event_id=_event_id(signal),
                        signal_id=signal.signal_id,
                        occurred_at_utc=close_time + _ENTRY_LATENCY,
                        symbol=signal.symbol,
                        action=signal.action.value,
                        status=PaperEventStatus.FILLED,
                        reason=None,
                        reference_price=reference,
                        execution_price=fill_price,
                        base_quantity=quantity,
                        quote_amount_usdt=net_quote,
                        fee_usdt=fee,
                        realized_pnl_usdt=realized,
                        breakout_strength=None,
                        strategy_version=signal.strategy_version,
                    )
                )
                del positions[point.symbol]

            candidates: list[tuple[Signal, IndicatorPoint]] = []
            for point in group:
                if not point.flip_up or point.symbol in positions:
                    continue
                signal = _signal(point, is_long=False)
                if signal is not None:
                    candidates.append((signal, point))
            order = {symbol: index for index, symbol in enumerate(SYMBOLS)}
            candidates.sort(
                key=lambda item: (
                    -(item[1].rank_strength or 0.0),
                    order[item[0].symbol],
                )
            )

            for signal, point in candidates:
                if settings.emergency_stop:
                    emitted.append(_blocked_event(signal, "EMERGENCY_STOP"))
                    continue
                if account.halted:
                    emitted.append(_blocked_event(signal, account.halt_reason or "HALTED"))
                    continue
                if daily_paused:
                    emitted.append(_blocked_event(signal, "DAILY_LOSS_5_PERCENT"))
                    continue
                if len(positions) >= settings.slot_count:
                    emitted.append(_blocked_event(signal, "NO_FREE_SLOT"))
                    continue
                rules = rules_by_symbol[signal.symbol]
                budget = min(settings.target_notional_usdt, account.cash_usdt)
                reference = _d(signal.close)
                fill_price = reference * (ONE + BASELINE_COSTS.adverse_price_rate)
                gross_quantity = _round_down(budget / fill_price, rules.step_size)
                quote_spend = gross_quantity * fill_price
                if gross_quantity < rules.min_qty or quote_spend < rules.min_notional:
                    emitted.append(_blocked_event(signal, "BELOW_EXCHANGE_MINIMUM"))
                    continue
                if quote_spend <= ZERO or quote_spend > account.cash_usdt:
                    emitted.append(_blocked_event(signal, "INSUFFICIENT_CASH"))
                    continue
                fee_base = gross_quantity * BASELINE_COSTS.fee_rate
                net_quantity = gross_quantity - fee_base
                fee_quote = fee_base * fill_price
                account = replace(account, cash_usdt=account.cash_usdt - quote_spend)
                position = PaperPosition(
                    symbol=signal.symbol,
                    quantity=net_quantity,
                    average_price=fill_price,
                    cost_basis_usdt=quote_spend,
                    entry_time_utc=close_time + _ENTRY_LATENCY,
                    entry_signal_id=signal.signal_id,
                    entry_fee_usdt=fee_quote,
                    updated_at_utc=close_time + _ENTRY_LATENCY,
                    strategy_version=signal.strategy_version,
                    slot_count=1,
                )
                positions[signal.symbol] = position
                emitted.append(
                    PaperEvent(
                        event_id=_event_id(signal),
                        signal_id=signal.signal_id,
                        occurred_at_utc=position.entry_time_utc,
                        symbol=signal.symbol,
                        action=signal.action.value,
                        status=PaperEventStatus.FILLED,
                        reason=None,
                        reference_price=reference,
                        execution_price=fill_price,
                        base_quantity=net_quantity,
                        quote_amount_usdt=quote_spend,
                        fee_usdt=fee_quote,
                        realized_pnl_usdt=None,
                        breakout_strength=(
                            _d(point.breakout_strength)
                            if point.breakout_strength is not None
                            else None
                        ),
                        strategy_version=signal.strategy_version,
                    )
                )

            checkpoints.update(
                {point.symbol: point.candle.close_time_utc for point in group}
            )

        if pending:
            final_time = max(pending)
            final_equity, _ = _equity(account.cash_usdt, positions, latest_prices)
            account, _, _ = _risk_account(account, equity=final_equity, at=final_time)
            store.apply_cycle(
                account=account,
                positions=positions,
                events=tuple(emitted),
                checkpoints=checkpoints,
                processed_bars=processed_bars,
            )
        return tuple(emitted)


def activate_paper_strategy(
    database_path: str,
    points_by_symbol: Mapping[str, tuple[IndicatorPoint, ...]],
    rules_by_symbol: Mapping[str, ExecutionRules],
    strategy: StrategyDefinition,
    *,
    at: datetime | None = None,
) -> tuple[PaperEvent, ...]:
    """Explicitly cut over paper at latest closed prices without deleting history."""

    if not strategy.paper_approved:
        raise ValueError(f"strategy {strategy.version} is not approved for paper")
    if set(points_by_symbol) != set(SYMBOLS) or set(rules_by_symbol) != set(SYMBOLS):
        raise ValueError("paper strategy activation requires all ten symbols")
    moment = (at or datetime.now(UTC)).astimezone(UTC)
    checkpoints = {
        symbol: points_by_symbol[symbol][-1].candle.close_time_utc for symbol in SYMBOLS
    }
    latest_prices = {
        symbol: _d(points_by_symbol[symbol][-1].candle.close) for symbol in SYMBOLS
    }
    with PaperStore(database_path) as store:
        store.initialize(at=moment)
        previous = store.load_strategy_session()
        if (
            previous.strategy_key == strategy.key
            and previous.strategy_version == strategy.version
        ):
            return ()
        account = store.load_account()
        positions = store.load_positions()
        events: list[PaperEvent] = []
        cash = account.cash_usdt
        for position in positions:
            rule = rules_by_symbol[position.symbol]
            reference = latest_prices[position.symbol]
            fill_price = reference * (ONE - BASELINE_COSTS.adverse_price_rate)
            quantity = _round_down(position.quantity, rule.step_size)
            gross_quote = quantity * fill_price
            if quantity < rule.min_qty or gross_quote < rule.min_notional:
                raise RuntimeError(
                    f"cannot activate strategy while {position.symbol} is exchange dust"
                )
            fee = gross_quote * BASELINE_COSTS.fee_rate
            net_quote = gross_quote - fee
            realized = net_quote - position.cost_basis_usdt
            signal_id = hashlib.sha256(
                (
                    f"PAPER_STRATEGY_SWITCH|{previous.strategy_version}|"
                    f"{strategy.version}|{position.symbol}|{moment.isoformat()}"
                ).encode()
            ).hexdigest()
            events.append(
                PaperEvent(
                    event_id=hashlib.sha256(f"PAPER|{signal_id}".encode()).hexdigest(),
                    signal_id=signal_id,
                    occurred_at_utc=moment,
                    symbol=position.symbol,
                    action="EXIT_LONG",
                    status=PaperEventStatus.FILLED,
                    reason=f"STRATEGY_SWITCH_TO_{strategy.version}",
                    reference_price=reference,
                    execution_price=fill_price,
                    base_quantity=quantity,
                    quote_amount_usdt=net_quote,
                    fee_usdt=fee,
                    realized_pnl_usdt=realized,
                    breakout_strength=None,
                    strategy_version=position.strategy_version,
                )
            )
            cash += net_quote
        activated_account = replace(
            account,
            cash_usdt=cash,
            high_water_equity_usdt=cash,
            day_start_equity_usdt=cash,
            day_start_date_utc=moment.date().isoformat(),
            halted=False,
            halt_reason=None,
            updated_at_utc=moment,
        )
        store.apply_strategy_activation(
            account=activated_account,
            events=tuple(events),
            checkpoints=checkpoints,
            strategy_key=strategy.key,
            strategy_version=strategy.version,
            starting_equity_usdt=cash,
            at=moment,
        )
    return tuple(events)


def load_paper_portfolio(
    database_path: str,
    latest_prices: Mapping[str, Decimal],
    *,
    at: datetime | None = None,
    strategy_key: str = "v1",
    strategy_version: str = HIXTON_SPEC_VERSION,
) -> PaperPortfolio:
    moment = (at or datetime.now(UTC)).astimezone(UTC)
    with PaperStore(database_path) as store:
        store.initialize(
            at=moment,
            strategy_key=strategy_key,
            strategy_version=strategy_version,
        )
        store.require_strategy(strategy_key, strategy_version)
        account = store.load_account()
        settings = store.load_settings()
        positions = store.load_positions()
    by_symbol = {position.symbol: position for position in positions}
    equity, unrealized = _equity(account.cash_usdt, by_symbol, latest_prices)
    account, daily_paused, drawdown_pct = _risk_account(account, equity=equity, at=moment)
    return PaperPortfolio(
        account=account,
        settings=settings,
        positions=positions,
        equity_usdt=equity,
        unrealized_pnl_usdt=unrealized,
        daily_loss_paused=daily_paused,
        drawdown_pct=drawdown_pct,
    )
