"""Chronological V1 backtest: signal at close, fill at next bar open."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_DOWN, Decimal

from hixton.backtest.metrics import calculate_metrics, drawdown
from hixton.backtest.models import (
    BASELINE_COSTS,
    ONE,
    ZERO,
    BacktestResult,
    BatchResult,
    CostModel,
    EquityPoint,
    ExecutionRules,
    Fill,
    Trade,
)
from hixton.constants import SYMBOLS, TIMEFRAME_DELTA
from hixton.data.quality import audit_candles
from hixton.domain.models import Candle, Signal, SignalAction
from hixton.domain.strategy import HixtonStrategy

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


def _snapshot_hash(candles: list[Candle]) -> str:
    digest = hashlib.sha256()
    for candle in candles:
        row = (
            candle.symbol,
            candle.open_time_utc.isoformat(),
            candle.close_time_utc.isoformat(),
            repr(candle.open),
            repr(candle.high),
            repr(candle.low),
            repr(candle.close),
            repr(candle.volume),
            repr(candle.quote_volume),
            candle.trade_count,
            candle.closed,
            candle.source,
        )
        digest.update(json.dumps(row, separators=(",", ":")).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _buy_and_hold(
    candles: list[Candle], starting_cash: Decimal, costs: CostModel
) -> Decimal:
    first_open = _d(candles[0].open)
    fill_price = first_open * (ONE + costs.adverse_price_rate)
    gross_quantity = starting_cash / fill_price
    net_quantity = gross_quantity * (ONE - costs.fee_rate)
    return net_quantity * _d(candles[-1].close)


def run_single_backtest(
    *,
    symbol: str,
    candles: list[Candle],
    report_start_utc: datetime,
    report_end_utc: datetime,
    starting_cash: Decimal = Decimal("250.00"),
    target_notional: Decimal = Decimal("250.00"),
    costs: CostModel = BASELINE_COSTS,
    execution_rules: ExecutionRules | None = None,
) -> BacktestResult:
    """Run an isolated no-compounding test and return immutable result records."""

    normalized = symbol.replace("/", "").upper()
    rules = execution_rules or ExecutionRules()
    if starting_cash <= ZERO or target_notional <= ZERO:
        raise ValueError("capital values must be positive")
    if report_start_utc >= report_end_utc:
        raise ValueError("report_start_utc must be before report_end_utc")
    warmup_start = report_start_utc - 400 * TIMEFRAME_DELTA
    selected = [
        candle
        for candle in candles
        if warmup_start <= candle.open_time_utc < report_end_utc
    ]
    quality = audit_candles(
        selected,
        expected_symbol=normalized,
        expected_start=warmup_start,
        expected_end_exclusive=report_end_utc,
    )
    quality.require_valid()

    strategy = HixtonStrategy(normalized)
    cash = starting_cash
    dust = ZERO
    open_trade: _OpenTrade | None = None
    pending_signal: Signal | None = None
    signals: list[Signal] = []
    fills: list[Fill] = []
    trades: list[Trade] = []
    equity_curve: list[EquityPoint] = []
    blocked: list[str] = []

    for candle in selected:
        in_report = report_start_utc <= candle.open_time_utc < report_end_utc
        if in_report and pending_signal is not None:
            if pending_signal.action is SignalAction.ENTER_LONG:
                if open_trade is not None:
                    raise RuntimeError("entry pending while already long")
                budget = min(target_notional, cash)
                reference = _d(candle.open)
                fill_price = reference * (ONE + costs.adverse_price_rate)
                gross_quantity = _round_down(budget / fill_price, rules.step_size)
                quote_spend = gross_quantity * fill_price
                if gross_quantity < rules.min_qty or quote_spend < rules.min_notional:
                    blocked.append(f"{pending_signal.signal_id}:BELOW_EXCHANGE_MINIMUM")
                elif quote_spend <= ZERO:
                    blocked.append(f"{pending_signal.signal_id}:NO_CASH")
                else:
                    fee_base = gross_quantity * costs.fee_rate
                    net_quantity = gross_quantity - fee_base
                    fee_quote = fee_base * fill_price
                    modeled_adverse = gross_quantity * (fill_price - reference)
                    fill = Fill(
                        signal_id=pending_signal.signal_id,
                        action=pending_signal.action,
                        fill_time_utc=candle.open_time_utc,
                        reference_open=reference,
                        fill_price=fill_price,
                        base_quantity=net_quantity,
                        quote_value=quote_spend,
                        fee_quote_equivalent=fee_quote,
                        modeled_spread_slippage=modeled_adverse,
                    )
                    cash -= quote_spend
                    open_trade = _OpenTrade(
                        signal=pending_signal,
                        fill=fill,
                        quantity=net_quantity,
                        cost_basis=quote_spend,
                    )
                    fills.append(fill)
            elif pending_signal.action is SignalAction.EXIT_LONG:
                if open_trade is None:
                    raise RuntimeError("exit pending while flat")
                reference = _d(candle.open)
                fill_price = reference * (ONE - costs.adverse_price_rate)
                sell_quantity = _round_down(open_trade.quantity, rules.step_size)
                gross_quote = sell_quantity * fill_price
                if sell_quantity < rules.min_qty or gross_quote < rules.min_notional:
                    blocked.append(f"{pending_signal.signal_id}:EXIT_BECAME_DUST")
                    dust += open_trade.quantity
                    open_trade = None
                else:
                    residual = open_trade.quantity - sell_quantity
                    fee_quote = gross_quote * costs.fee_rate
                    net_quote = gross_quote - fee_quote
                    modeled_adverse = sell_quantity * (reference - fill_price)
                    basis_fraction = (
                        sell_quantity / open_trade.quantity
                        if open_trade.quantity > ZERO
                        else ZERO
                    )
                    realized_basis = open_trade.cost_basis * basis_fraction
                    realized_pnl = net_quote - realized_basis
                    fill = Fill(
                        signal_id=pending_signal.signal_id,
                        action=pending_signal.action,
                        fill_time_utc=candle.open_time_utc,
                        reference_open=reference,
                        fill_price=fill_price,
                        base_quantity=sell_quantity,
                        quote_value=gross_quote,
                        fee_quote_equivalent=fee_quote,
                        modeled_spread_slippage=modeled_adverse,
                    )
                    cash += net_quote
                    dust += residual
                    fills.append(fill)
                    holding_hours = Decimal(
                        str(
                            (candle.open_time_utc - open_trade.fill.fill_time_utc).total_seconds()
                            / 3_600
                        )
                    )
                    trades.append(
                        Trade(
                            symbol=normalized,
                            entry_signal_id=open_trade.signal.signal_id,
                            exit_signal_id=pending_signal.signal_id,
                            entry_time_utc=open_trade.fill.fill_time_utc,
                            exit_time_utc=candle.open_time_utc,
                            entry_quote_spend=realized_basis,
                            exit_quote_receive=net_quote,
                            realized_pnl=realized_pnl,
                            realized_return_pct=(realized_pnl / realized_basis * _HUNDRED),
                            entry_price=open_trade.fill.fill_price,
                            exit_price=fill_price,
                            sold_base_quantity=sell_quantity,
                            residual_dust_quantity=residual,
                            holding_hours=holding_hours,
                        )
                    )
                    open_trade = None
            pending_signal = None

        point = strategy.update(candle)
        if not in_report:
            continue

        signal = strategy.signal_for(point, is_long=open_trade is not None)
        if signal is not None:
            signals.append(signal)
            pending_signal = signal

        active_quantity = open_trade.quantity if open_trade is not None else ZERO
        position_value = (active_quantity + dust) * _d(candle.close)
        equity_curve.append(
            EquityPoint(
                time_utc=candle.close_time_utc,
                cash=cash,
                position_value=position_value,
                equity=cash + position_value,
                active_position=open_trade is not None,
            )
        )

    if not equity_curve:
        raise ValueError("report window did not contain candles")
    ending_equity = equity_curve[-1].equity
    report_candles = [
        candle
        for candle in selected
        if report_start_utc <= candle.open_time_utc < report_end_utc
    ]
    buy_hold = _buy_and_hold(report_candles, starting_cash, costs)
    metrics = calculate_metrics(
        starting_equity=starting_cash,
        ending_equity=ending_equity,
        report_start_utc=report_start_utc,
        report_end_utc=report_end_utc,
        trades=tuple(trades),
        fills=tuple(fills),
        equity_curve=tuple(equity_curve),
        buy_and_hold_ending_equity=buy_hold,
    )
    active_quantity = open_trade.quantity if open_trade is not None else ZERO
    return BacktestResult(
        symbol=normalized,
        report_start_utc=report_start_utc,
        report_end_utc=report_end_utc,
        warmup_start_utc=warmup_start,
        cost_model=costs,
        starting_cash=starting_cash,
        target_notional=target_notional,
        signals=tuple(signals),
        fills=tuple(fills),
        trades=tuple(trades),
        equity_curve=tuple(equity_curve),
        blocked_signals=tuple(blocked),
        pending_signal_at_end=pending_signal,
        open_position_at_end=open_trade is not None,
        open_position_quantity=active_quantity,
        dust_quantity=dust,
        metrics=metrics,
        data_snapshot_sha256=_snapshot_hash(selected),
    )


def run_isolated_batch(
    *,
    candles_by_symbol: dict[str, list[Candle]],
    report_start_utc: datetime,
    report_end_utc: datetime,
    costs: CostModel = BASELINE_COSTS,
    execution_rules: dict[str, ExecutionRules] | None = None,
) -> BatchResult:
    if len(candles_by_symbol) != len(SYMBOLS) or set(candles_by_symbol) != set(SYMBOLS):
        raise ValueError("batch input must contain all ten symbols in the fixed DMS order")
    rules = execution_rules or {}
    results = tuple(
        run_single_backtest(
            symbol=symbol,
            candles=candles_by_symbol[symbol],
            report_start_utc=report_start_utc,
            report_end_utc=report_end_utc,
            costs=costs,
            execution_rules=rules.get(symbol),
        )
        for symbol in SYMBOLS
    )
    starting = sum((result.metrics.starting_equity for result in results), ZERO)
    ending = sum((result.metrics.ending_equity for result in results), ZERO)
    synchronized: dict[datetime, Decimal] = {}
    for result in results:
        for point in result.equity_curve:
            synchronized[point.time_utc] = synchronized.get(point.time_utc, ZERO) + point.equity
    combined_curve = tuple(
        EquityPoint(time, ZERO, ZERO, equity, False)
        for time, equity in sorted(synchronized.items())
    )
    max_drawdown, max_drawdown_pct = drawdown(combined_curve)
    return BatchResult(
        results=results,
        starting_equity=starting,
        ending_equity=ending,
        net_pnl=ending - starting,
        return_pct=(ending / starting - ONE) * _HUNDRED,
        completed_trades=sum(result.metrics.completed_trades for result in results),
        max_drawdown=max_drawdown,
        max_drawdown_pct=max_drawdown_pct,
    )
