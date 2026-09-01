from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest

from hixton.backtest.engine import run_isolated_batch, run_single_backtest
from hixton.backtest.models import (
    BASELINE_COSTS,
    STRESS_COSTS,
    BacktestResult,
    CostModel,
    ExecutionRules,
)
from hixton.constants import SYMBOLS
from hixton.domain.models import Candle, SignalAction
from tests.golden_reference import deterministic_candles


def _single(costs: CostModel = BASELINE_COSTS) -> tuple[list[Candle], BacktestResult]:
    candles = deterministic_candles("ETHUSDT", 1_200, 1)
    return candles, run_single_backtest(
        symbol="ETHUSDT",
        candles=candles,
        report_start_utc=candles[400].open_time_utc,
        report_end_utc=candles[-1].open_time_utc + timedelta(hours=1),
        costs=costs,
    )


def test_fills_occur_at_next_bar_open_without_lookahead() -> None:
    candles, result = _single()
    by_signal = {fill.signal_id: fill for fill in result.fills}
    assert result.fills
    for signal in result.signals:
        fill = by_signal.get(signal.signal_id)
        if fill is None:
            continue
        expected = candles[signal.point_index + 1]
        assert fill.fill_time_utc == expected.open_time_utc
        assert fill.reference_open == Decimal(str(expected.open))


def test_isolated_target_does_not_compound_and_cash_never_goes_negative() -> None:
    _, result = _single()
    entries = [fill for fill in result.fills if fill.action is SignalAction.ENTER_LONG]
    assert len(entries) >= 2
    assert all(fill.quote_value <= Decimal("250.00") for fill in entries)
    assert all(point.cash >= 0 for point in result.equity_curve)
    assert result.metrics.starting_equity == Decimal("250.00")


def test_stress_costs_are_reported_and_reduce_same_strategy_result() -> None:
    _, baseline = _single(BASELINE_COSTS)
    _, stress = _single(STRESS_COSTS)
    assert [signal.signal_id for signal in baseline.signals] == [
        signal.signal_id for signal in stress.signals
    ]
    assert stress.metrics.modeled_spread_slippage > baseline.metrics.modeled_spread_slippage
    assert stress.metrics.ending_equity < baseline.metrics.ending_equity


def test_final_signal_is_not_filled_outside_report_window() -> None:
    candles, full = _single()
    last_signal = full.signals[-1]
    end_exclusive = candles[last_signal.point_index].open_time_utc + timedelta(hours=1)
    partial = run_single_backtest(
        symbol="ETHUSDT",
        candles=candles,
        report_start_utc=candles[400].open_time_utc,
        report_end_utc=end_exclusive,
    )
    assert partial.pending_signal_at_end is not None
    assert partial.pending_signal_at_end.signal_id == last_signal.signal_id
    assert all(fill.signal_id != last_signal.signal_id for fill in partial.fills)


def test_exchange_minimum_blocks_entry_instead_of_inventing_fill() -> None:
    candles = deterministic_candles("BTCUSDT", 1_000)
    result = run_single_backtest(
        symbol="BTCUSDT",
        candles=candles,
        report_start_utc=candles[400].open_time_utc,
        report_end_utc=candles[-1].open_time_utc + timedelta(hours=1),
        execution_rules=ExecutionRules(min_notional=Decimal("1000")),
    )
    assert not result.fills
    assert result.blocked_signals
    assert result.metrics.ending_equity == Decimal("250.00")


def test_batch_runs_exactly_ten_isolated_250_usdt_ledgers() -> None:
    candles_by_symbol = {
        symbol: deterministic_candles(symbol, 1_000, market_index)
        for market_index, symbol in enumerate(SYMBOLS)
    }
    first = candles_by_symbol[SYMBOLS[0]]
    batch = run_isolated_batch(
        candles_by_symbol=candles_by_symbol,
        report_start_utc=first[400].open_time_utc,
        report_end_utc=first[-1].open_time_utc + timedelta(hours=1),
    )
    assert len(batch.results) == 10
    assert batch.starting_equity == Decimal("2500.00")
    assert [result.symbol for result in batch.results] == list(SYMBOLS)
    assert all(result.starting_cash == Decimal("250.00") for result in batch.results)


def test_batch_rejects_missing_market() -> None:
    with pytest.raises(ValueError, match="all ten"):
        run_isolated_batch(
            candles_by_symbol={"BTCUSDT": deterministic_candles("BTCUSDT", 500)},
            report_start_utc=deterministic_candles("BTCUSDT", 500)[400].open_time_utc,
            report_end_utc=deterministic_candles("BTCUSDT", 500)[-1].open_time_utc
            + timedelta(hours=1),
        )
