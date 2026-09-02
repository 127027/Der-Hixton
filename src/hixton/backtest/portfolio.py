"""Chronological shared-cash 3x80 portfolio backtest for all DMS markets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_DOWN, Decimal

from hixton.backtest.engine import candle_snapshot_sha256
from hixton.backtest.metrics import calculate_metrics
from hixton.backtest.models import (
    BASELINE_COSTS,
    ONE,
    ZERO,
    CostModel,
    EquityPoint,
    ExecutionRules,
    Fill,
    PortfolioBacktestResult,
    Trade,
)
from hixton.constants import SYMBOLS, TIMEFRAME_DELTA
from hixton.data.quality import audit_candles
from hixton.domain.models import Candle, Signal, SignalAction, StrategyParameters, StrategySemantics
from hixton.domain.strategy import HixtonStrategy, rank_strength

_HUNDRED = Decimal("100")


@dataclass(slots=True)
class _OpenTrade:
    signal: Signal
    fill: Fill
    quantity: Decimal
    cost_basis: Decimal


def _d(value: float) -> Decimal:
    return Decimal(str(value))


def _round_down(value: Decimal, step: Decimal) -> Decimal:
    if step <= ZERO:
        return value
    return (value / step).to_integral_value(rounding=ROUND_DOWN) * step


def _equal_weight_buy_and_hold(
    candles_by_symbol: dict[str, list[Candle]],
    starting_cash: Decimal,
    costs: CostModel,
) -> Decimal:
    allocation = starting_cash / Decimal(len(SYMBOLS))
    ending = ZERO
    for symbol in SYMBOLS:
        candles = candles_by_symbol[symbol]
        entry = _d(candles[0].open) * (ONE + costs.adverse_price_rate)
        net_quantity = allocation / entry * (ONE - costs.fee_rate)
        ending += net_quantity * _d(candles[-1].close)
    return ending


def run_shared_portfolio_backtest(
    *,
    candles_by_symbol: dict[str, list[Candle]],
    report_start_utc: datetime,
    report_end_utc: datetime,
    starting_cash: Decimal = Decimal("240.00"),
    target_notional: Decimal = Decimal("80.00"),
    slot_count: int = 3,
    costs: CostModel = BASELINE_COSTS,
    execution_rules: dict[str, ExecutionRules] | None = None,
    strategy_parameters: StrategyParameters | None = None,
    strategy_semantics: StrategySemantics = StrategySemantics.DMS_V1,
    strategy_version: str | None = None,
) -> PortfolioBacktestResult:
    """Replay ten aligned markets against one non-compounding shared ledger."""

    if tuple(candles_by_symbol) != SYMBOLS:
        raise ValueError("portfolio input must contain all ten symbols in fixed DMS order")
    if starting_cash <= ZERO or target_notional <= ZERO or slot_count <= 0:
        raise ValueError("portfolio capital and slot_count must be positive")
    if report_start_utc >= report_end_utc:
        raise ValueError("report_start_utc must be before report_end_utc")

    parameters = strategy_parameters or StrategyParameters()
    warmup_start = report_start_utc - parameters.warmup_bars * TIMEFRAME_DELTA
    selected_by_symbol: dict[str, list[Candle]] = {}
    report_by_symbol: dict[str, list[Candle]] = {}
    rules = execution_rules or {}
    for symbol in SYMBOLS:
        selected = [
            candle
            for candle in candles_by_symbol[symbol]
            if warmup_start <= candle.open_time_utc < report_end_utc
        ]
        audit_candles(
            selected,
            expected_symbol=symbol,
            expected_start=warmup_start,
            expected_end_exclusive=report_end_utc,
        ).require_valid()
        selected_by_symbol[symbol] = selected
        report_by_symbol[symbol] = [
            candle for candle in selected if candle.open_time_utc >= report_start_utc
        ]

    rows = tuple(zip(*(selected_by_symbol[symbol] for symbol in SYMBOLS), strict=True))
    for row in rows:
        if len({candle.open_time_utc for candle in row}) != 1:
            raise ValueError("portfolio candles are not aligned by open_time_utc")

    strategies = {
        symbol: HixtonStrategy(
            symbol,
            parameters=parameters,
            semantics=strategy_semantics,
            strategy_version=strategy_version,
        )
        for symbol in SYMBOLS
    }
    cash = starting_cash
    positions: dict[str, _OpenTrade] = {}
    dust = dict.fromkeys(SYMBOLS, ZERO)
    pending: list[Signal] = []
    signals: list[Signal] = []
    fills: list[Fill] = []
    trades: list[Trade] = []
    equity_curve: list[EquityPoint] = []
    blocked: list[str] = []
    max_concurrent = 0
    order = {symbol: index for index, symbol in enumerate(SYMBOLS)}

    for row in rows:
        open_time = row[0].open_time_utc
        in_report = report_start_utc <= open_time < report_end_utc
        candles = {candle.symbol: candle for candle in row}

        if in_report and pending:
            exits = [signal for signal in pending if signal.action is SignalAction.EXIT_LONG]
            entries = [signal for signal in pending if signal.action is SignalAction.ENTER_LONG]

            for signal in exits:
                open_trade = positions.get(signal.symbol)
                if open_trade is None:
                    blocked.append(f"{signal.signal_id}:POSITION_ALREADY_CLOSED")
                    continue
                rule = rules.get(signal.symbol, ExecutionRules())
                reference = _d(candles[signal.symbol].open)
                fill_price = reference * (ONE - costs.adverse_price_rate)
                sell_quantity = _round_down(open_trade.quantity, rule.step_size)
                gross_quote = sell_quantity * fill_price
                if sell_quantity < rule.min_qty or gross_quote < rule.min_notional:
                    blocked.append(f"{signal.signal_id}:EXIT_BECAME_DUST")
                    dust[signal.symbol] += open_trade.quantity
                    del positions[signal.symbol]
                    continue
                residual = open_trade.quantity - sell_quantity
                fee_quote = gross_quote * costs.fee_rate
                net_quote = gross_quote - fee_quote
                modeled_adverse = sell_quantity * (reference - fill_price)
                basis_fraction = sell_quantity / open_trade.quantity
                realized_basis = open_trade.cost_basis * basis_fraction
                realized_pnl = net_quote - realized_basis
                fill = Fill(
                    signal_id=signal.signal_id,
                    action=signal.action,
                    fill_time_utc=open_time,
                    reference_open=reference,
                    fill_price=fill_price,
                    base_quantity=sell_quantity,
                    quote_value=gross_quote,
                    fee_quote_equivalent=fee_quote,
                    modeled_spread_slippage=modeled_adverse,
                )
                cash += net_quote
                dust[signal.symbol] += residual
                fills.append(fill)
                holding_hours = Decimal(
                    str((open_time - open_trade.fill.fill_time_utc).total_seconds() / 3_600)
                )
                trades.append(
                    Trade(
                        symbol=signal.symbol,
                        entry_signal_id=open_trade.signal.signal_id,
                        exit_signal_id=signal.signal_id,
                        entry_time_utc=open_trade.fill.fill_time_utc,
                        exit_time_utc=open_time,
                        entry_quote_spend=realized_basis,
                        exit_quote_receive=net_quote,
                        realized_pnl=realized_pnl,
                        realized_return_pct=realized_pnl / realized_basis * _HUNDRED,
                        entry_price=open_trade.fill.fill_price,
                        exit_price=fill_price,
                        sold_base_quantity=sell_quantity,
                        residual_dust_quantity=residual,
                        holding_hours=holding_hours,
                    )
                )
                del positions[signal.symbol]

            entries.sort(
                key=lambda signal: (
                    -rank_strength(signal.breakout_strength or 0.0),
                    order[signal.symbol],
                )
            )
            for signal in entries:
                if signal.symbol in positions:
                    blocked.append(f"{signal.signal_id}:POSITION_ALREADY_OPEN")
                    continue
                if len(positions) >= slot_count:
                    blocked.append(f"{signal.signal_id}:NO_FREE_SLOT")
                    continue
                rule = rules.get(signal.symbol, ExecutionRules())
                budget = min(target_notional, cash)
                reference = _d(candles[signal.symbol].open)
                fill_price = reference * (ONE + costs.adverse_price_rate)
                gross_quantity = _round_down(budget / fill_price, rule.step_size)
                quote_spend = min(gross_quantity * fill_price, budget)
                if gross_quantity < rule.min_qty or quote_spend < rule.min_notional:
                    blocked.append(f"{signal.signal_id}:BELOW_EXCHANGE_MINIMUM")
                    continue
                if quote_spend <= ZERO or quote_spend > cash:
                    blocked.append(f"{signal.signal_id}:INSUFFICIENT_CASH")
                    continue
                fee_base = gross_quantity * costs.fee_rate
                net_quantity = gross_quantity - fee_base
                fee_quote = fee_base * fill_price
                modeled_adverse = gross_quantity * (fill_price - reference)
                fill = Fill(
                    signal_id=signal.signal_id,
                    action=signal.action,
                    fill_time_utc=open_time,
                    reference_open=reference,
                    fill_price=fill_price,
                    base_quantity=net_quantity,
                    quote_value=quote_spend,
                    fee_quote_equivalent=fee_quote,
                    modeled_spread_slippage=modeled_adverse,
                )
                cash -= quote_spend
                positions[signal.symbol] = _OpenTrade(signal, fill, net_quantity, quote_spend)
                fills.append(fill)
            pending = []

        new_pending: list[Signal] = []
        for symbol in SYMBOLS:
            point = strategies[symbol].update(candles[symbol])
            if not in_report:
                continue
            new_signal = strategies[symbol].signal_for(point, is_long=symbol in positions)
            if new_signal is not None:
                signals.append(new_signal)
                new_pending.append(new_signal)
        if in_report:
            pending = new_pending
            max_concurrent = max(max_concurrent, len(positions))
            position_value = sum(
                (
                    (
                        (positions[symbol].quantity if symbol in positions else ZERO)
                        + dust[symbol]
                    )
                    * _d(candles[symbol].close)
                    for symbol in SYMBOLS
                ),
                ZERO,
            )
            equity_curve.append(
                EquityPoint(
                    time_utc=max(candle.close_time_utc for candle in row),
                    cash=cash,
                    position_value=position_value,
                    equity=cash + position_value,
                    active_position=bool(positions),
                )
            )

    if not equity_curve:
        raise ValueError("report window did not contain candles")
    metrics = calculate_metrics(
        starting_equity=starting_cash,
        ending_equity=equity_curve[-1].equity,
        report_start_utc=report_start_utc,
        report_end_utc=report_end_utc,
        trades=tuple(trades),
        fills=tuple(fills),
        equity_curve=tuple(equity_curve),
        buy_and_hold_ending_equity=_equal_weight_buy_and_hold(
            report_by_symbol, starting_cash, costs
        ),
    )
    return PortfolioBacktestResult(
        symbols=SYMBOLS,
        report_start_utc=report_start_utc,
        report_end_utc=report_end_utc,
        warmup_start_utc=warmup_start,
        cost_model=costs,
        starting_cash=starting_cash,
        target_notional=target_notional,
        slot_count=slot_count,
        signals=tuple(signals),
        fills=tuple(fills),
        trades=tuple(trades),
        equity_curve=tuple(equity_curve),
        blocked_signals=tuple(blocked),
        pending_signals_at_end=tuple(pending),
        open_symbols_at_end=tuple(symbol for symbol in SYMBOLS if symbol in positions),
        dust_quantity_by_symbol=dust,
        max_concurrent_positions=max_concurrent,
        metrics=metrics,
        data_snapshot_sha256_by_symbol={
            symbol: candle_snapshot_sha256(selected_by_symbol[symbol]) for symbol in SYMBOLS
        },
    )
