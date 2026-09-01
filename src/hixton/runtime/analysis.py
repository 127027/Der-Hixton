"""Rebuild the canonical 1h indicator cache from validated local candles."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from hixton.constants import SYMBOLS
from hixton.data.quality import DataQualityReport, audit_candles
from hixton.data.storage import CandleStore
from hixton.domain.models import IndicatorPoint
from hixton.domain.strategy import evaluate_batch


def rebuild_analysis(
    database_path: Path,
    *,
    start: datetime,
    end_exclusive: datetime,
) -> tuple[
    dict[str, tuple[IndicatorPoint, ...]],
    dict[str, DataQualityReport],
]:
    points_by_symbol: dict[str, tuple[IndicatorPoint, ...]] = {}
    quality_by_symbol: dict[str, DataQualityReport] = {}
    with CandleStore(database_path) as store:
        if not store.integrity_check():
            raise RuntimeError("SQLite integrity check failed")
        for symbol in SYMBOLS:
            candles = store.load_candles(
                symbol,
                start=start,
                end_exclusive=end_exclusive,
            )
            quality = audit_candles(
                candles,
                expected_symbol=symbol,
                expected_start=start,
                expected_end_exclusive=end_exclusive,
            )
            quality.require_valid()
            points_by_symbol[symbol] = tuple(evaluate_batch(symbol, candles))
            quality_by_symbol[symbol] = quality
    return points_by_symbol, quality_by_symbol

