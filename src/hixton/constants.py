"""Project-wide constants fixed by DMS V1."""

from __future__ import annotations

from datetime import timedelta

HIXTON_SPEC_VERSION = "HIXTON-SPEC-1.0"
STRATEGY_ID = "hixton_vidya_atr"
EXCHANGE = "binance_spot"
TIMEFRAME = "1h"
TIMEFRAME_DELTA = timedelta(hours=1)

SYMBOLS: tuple[str, ...] = (
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "LINKUSDT",
    "AVAXUSDT",
    "DOTUSDT",
    "DOGEUSDT",
)

SYMBOL_TIE_BREAK: dict[str, int] = {symbol: rank for rank, symbol in enumerate(SYMBOLS)}

