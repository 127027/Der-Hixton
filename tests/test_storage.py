from __future__ import annotations

from dataclasses import replace
from datetime import timedelta

from hixton.data.storage import CandleStore
from tests.golden_reference import deterministic_candles


def test_store_is_idempotent_and_keeps_revision_history(tmp_path) -> None:
    path = tmp_path / "market.sqlite3"
    candles = deterministic_candles("BTCUSDT", 4)
    with CandleStore(path) as store:
        first = store.put_candles(candles)
        second = store.put_candles(candles)
        revised_candle = replace(candles[2], close=candles[2].close + 0.25)
        revised = store.put_candles([revised_candle], revision_reason="provider_revision")
        loaded = store.load_candles("BTCUSDT")

        assert first.inserted == 4
        assert second.unchanged == 4
        assert revised.revised == 1
        assert store.revision_count() == 1
        assert loaded[2].close == revised_candle.close
        assert store.integrity_check()


def test_snapshot_hash_is_stable_and_window_sensitive(tmp_path) -> None:
    candles = deterministic_candles("ETHUSDT", 10, 1)
    with CandleStore(tmp_path / "market.sqlite3") as store:
        store.put_candles(candles)
        full_end = candles[-1].open_time_utc + timedelta(hours=1)
        full_a = store.snapshot_sha256(
            "ETHUSDT", start=candles[0].open_time_utc, end_exclusive=full_end
        )
        full_b = store.snapshot_sha256(
            "ETHUSDT", start=candles[0].open_time_utc, end_exclusive=full_end
        )
        shorter = store.snapshot_sha256(
            "ETHUSDT", start=candles[1].open_time_utc, end_exclusive=full_end
        )

    assert full_a == full_b
    assert full_a != shorter


def test_closed_only_excludes_provisional_candle(tmp_path) -> None:
    candles = deterministic_candles("BNBUSDT", 2, 2)
    provisional = replace(candles[1], closed=False)
    with CandleStore(tmp_path / "market.sqlite3") as store:
        store.put_candles([candles[0], provisional])
        assert len(store.load_candles("BNBUSDT")) == 1
        assert len(store.load_candles("BNBUSDT", closed_only=False)) == 2

