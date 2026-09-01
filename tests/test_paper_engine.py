from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from hixton.backtest.models import ExecutionRules
from hixton.constants import SYMBOLS
from hixton.domain.models import Candle, IndicatorPoint, TrendState
from hixton.paper.engine import initialize_paper_at_latest, process_new_closed_points
from hixton.paper.models import PaperEvent, PaperEventStatus, PaperSettings
from hixton.paper.storage import PaperStore


def _point(
    symbol: str,
    close_time: datetime,
    *,
    flip_up: bool = False,
    flip_down: bool = False,
    strength: float | None = None,
) -> IndicatorPoint:
    open_time = close_time - timedelta(hours=1)
    candle = Candle(
        symbol=symbol,
        open_time_utc=open_time,
        close_time_utc=close_time,
        open=100.0,
        high=102.0,
        low=98.0,
        close=101.0,
        volume=10.0,
    )
    return IndicatorPoint(
        symbol=symbol,
        index=500,
        candle=candle,
        abs_cmo=0.5,
        vidya_raw=100.0,
        vidya=100.0,
        true_range=4.0,
        atr=1.0,
        upper=100.5,
        lower=99.5,
        trend=TrendState.UP if flip_up else TrendState.DOWN,
        flip_up=flip_up,
        flip_down=flip_down,
        breakout_strength=strength,
        rank_strength=strength,
        tradable=True,
    )


def _mapping(at: datetime) -> dict[str, tuple[IndicatorPoint, ...]]:
    return {symbol: (_point(symbol, at),) for symbol in SYMBOLS}


def _rules() -> dict[str, ExecutionRules]:
    rules = ExecutionRules(
        step_size=Decimal("0.000001"),
        min_qty=Decimal("0.000001"),
        min_notional=Decimal("5"),
    )
    return dict.fromkeys(SYMBOLS, rules)


def test_startup_arms_at_latest_without_historical_orders(tmp_path: Path) -> None:
    path = tmp_path / "paper.sqlite3"
    start = datetime(2026, 1, 1, 0, tzinfo=UTC)
    points = {
        symbol: (_point(symbol, start, flip_up=True, strength=1.0),)
        for symbol in SYMBOLS
    }
    assert initialize_paper_at_latest(str(path), points, at=start) is True
    emitted = process_new_closed_points(str(path), points, _rules())
    assert emitted == ()
    with PaperStore(path) as store:
        assert store.load_account().cash_usdt == Decimal("240.00")
        assert store.load_positions() == ()


def test_restart_preserves_checkpoint_and_recovers_closed_bars(tmp_path: Path) -> None:
    path = tmp_path / "paper.sqlite3"
    start = datetime(2026, 1, 1, 0, tzinfo=UTC)
    assert initialize_paper_at_latest(str(path), _mapping(start), at=start) is True

    recovered_at = start + timedelta(hours=1)
    recovered = _mapping(recovered_at)
    recovered[SYMBOLS[0]] = (
        _point(SYMBOLS[0], recovered_at, flip_up=True, strength=2.0),
    )
    assert initialize_paper_at_latest(str(path), recovered, at=recovered_at) is False
    with PaperStore(path) as store:
        assert store.checkpoint(SYMBOLS[0]) == start

    emitted = process_new_closed_points(str(path), recovered, _rules())
    assert [(event.symbol, event.action) for event in emitted] == [
        (SYMBOLS[0], "ENTER_LONG")
    ]
    with PaperStore(path) as store:
        assert store.checkpoint(SYMBOLS[0]) == recovered_at
        progress = store.load_soak_progress(at=recovered_at)
    assert progress.minimum_processed_closed_bars == 1
    assert progress.processed_closed_bars_by_symbol[SYMBOLS[0]] == 1


def test_paper_soak_gate_is_persistent_and_requires_all_three_thresholds(
    tmp_path: Path,
) -> None:
    path = tmp_path / "paper.sqlite3"
    start = datetime(2026, 1, 1, 0, tzinfo=UTC)
    initialize_paper_at_latest(str(path), _mapping(start), at=start)
    events = tuple(
        PaperEvent(
            event_id=f"event-{index}",
            signal_id=f"signal-{index}",
            occurred_at_utc=start + timedelta(hours=index + 1),
            symbol=SYMBOLS[index % len(SYMBOLS)],
            action="EXIT_LONG",
            status=PaperEventStatus.FILLED,
            reason=None,
            reference_price=Decimal("100"),
            execution_price=Decimal("100"),
            base_quantity=Decimal("1"),
            quote_amount_usdt=Decimal("100"),
            fee_usdt=Decimal("0.10"),
            realized_pnl_usdt=Decimal("1"),
            breakout_strength=None,
        )
        for index in range(20)
    )
    end = start + timedelta(hours=720)
    with PaperStore(path) as store:
        store.apply_cycle(
            account=store.load_account(),
            positions={},
            events=events,
            checkpoints=dict.fromkeys(SYMBOLS, end),
            processed_bars=dict.fromkeys(SYMBOLS, 720),
        )
        progress = store.load_soak_progress(at=start + timedelta(days=30))
    assert progress.ready is True
    assert progress.status == "PASSED"
    assert progress.calendar_days == 30
    assert progress.minimum_processed_closed_bars == 720
    assert progress.completed_trades == 20
    assert progress.blockers == ()


def test_slot_priority_is_deterministic_and_cycle_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "paper.sqlite3"
    start = datetime(2026, 1, 1, 0, tzinfo=UTC)
    initialize_paper_at_latest(str(path), _mapping(start), at=start)
    signal_time = start + timedelta(hours=1)
    points = _mapping(signal_time)
    for symbol in SYMBOLS[:5]:
        points[symbol] = (_point(symbol, signal_time, flip_up=True, strength=1.0),)

    emitted = process_new_closed_points(str(path), points, _rules())
    filled = [event for event in emitted if event.status is PaperEventStatus.FILLED]
    blocked = [event for event in emitted if event.status is PaperEventStatus.BLOCKED]
    assert [event.symbol for event in filled] == list(SYMBOLS[:3])
    assert [event.symbol for event in blocked] == list(SYMBOLS[3:5])
    assert all(event.reason == "NO_FREE_SLOT" for event in blocked)

    assert process_new_closed_points(str(path), points, _rules()) == ()
    with PaperStore(path) as store:
        positions = store.load_positions()
        assert [position.symbol for position in positions] == sorted(SYMBOLS[:3])
        assert store.load_account().cash_usdt >= Decimal("0")
        assert len(store.load_events()) == 5


def test_exit_frees_slot_before_same_bar_entry(tmp_path: Path) -> None:
    path = tmp_path / "paper.sqlite3"
    start = datetime(2026, 1, 1, 0, tzinfo=UTC)
    initialize_paper_at_latest(str(path), _mapping(start), at=start)
    first = start + timedelta(hours=1)
    entries = _mapping(first)
    for symbol in SYMBOLS[:3]:
        entries[symbol] = (_point(symbol, first, flip_up=True, strength=1.0),)
    process_new_closed_points(str(path), entries, _rules())

    second = first + timedelta(hours=1)
    cycle = _mapping(second)
    cycle[SYMBOLS[0]] = (_point(SYMBOLS[0], second, flip_down=True),)
    cycle[SYMBOLS[3]] = (_point(SYMBOLS[3], second, flip_up=True, strength=2.0),)
    emitted = process_new_closed_points(str(path), cycle, _rules())
    assert [(event.symbol, event.action) for event in emitted] == [
        (SYMBOLS[0], "EXIT_LONG"),
        (SYMBOLS[3], "ENTER_LONG"),
    ]
    with PaperStore(path) as store:
        assert {position.symbol for position in store.load_positions()} == {
            SYMBOLS[1],
            SYMBOLS[2],
            SYMBOLS[3],
        }


def test_paper_settings_enforce_shared_capital() -> None:
    with pytest.raises(ValueError, match="240"):
        PaperSettings(slot_count=4, target_notional_usdt=Decimal("80"))
