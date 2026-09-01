from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from hixton.backtest.models import ExecutionRules
from hixton.constants import SYMBOLS
from hixton.domain.models import Candle, IndicatorPoint, TrendState
from hixton.paper.engine import initialize_paper_at_latest, process_new_closed_points
from hixton.paper.models import PaperEventStatus, PaperSettings
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
    initialize_paper_at_latest(str(path), points, at=start)
    emitted = process_new_closed_points(str(path), points, _rules())
    assert emitted == ()
    with PaperStore(path) as store:
        assert store.load_account().cash_usdt == Decimal("240.00")
        assert store.load_positions() == ()


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
