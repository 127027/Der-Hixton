"""Canonical USDC market universe for the active bot runtime."""

from __future__ import annotations

from hixton.constants import BASE_ASSETS, QUOTE_ASSET, SYMBOLS


def symbols_for_quote(quote_asset: str) -> tuple[str, ...]:
    if quote_asset.upper() != QUOTE_ASSET:
        raise ValueError(f"Only {QUOTE_ASSET} is supported by the active runtime")
    return tuple(base + QUOTE_ASSET for base in BASE_ASSETS)


def validate_market_symbols(symbols: tuple[str, ...]) -> str:
    if symbols != SYMBOLS:
        raise ValueError("Ten ordered USDC markets required")
    return QUOTE_ASSET
