"""Explicit quote currencies; historical USDT records are never renamed to USDC."""

from __future__ import annotations

from hixton.constants import SYMBOLS

BASE_ASSETS = tuple(symbol.removesuffix("USDT") for symbol in SYMBOLS)


def symbols_for_quote(quote_asset: str) -> tuple[str, ...]:
    if quote_asset not in {"USDT", "USDC"}:
        raise ValueError("Supported quote currencies are USDT and USDC")
    return tuple(base + quote_asset for base in BASE_ASSETS)


def split_market(symbol: str) -> tuple[str, str]:
    """Strict asset identity, not a permissive suffix replacement."""
    for quote in ("USDT", "USDC"):
        if symbol in symbols_for_quote(quote):
            return symbol.removesuffix(quote), quote
    raise ValueError("Unsupported Hixton Spot market")


def validate_market_symbols(symbols: tuple[str, ...]) -> str:
    for quote in ("USDT", "USDC"):
        if symbols == symbols_for_quote(quote):
            return quote
    raise ValueError("Ten ordered, unmixed USDT or USDC markets required")
