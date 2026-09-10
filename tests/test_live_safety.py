from __future__ import annotations

from decimal import Decimal as D

import pytest

from hixton.live.orders import TrialIntent
from hixton.live.safety import TrialPreSubmitGuard, TrialSafetyError


class Transport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, str]]] = []
        self.bid = "99.99"
        self.ask = "100.01"
        self.free_usdc = "100"
        self.free_base = "0.500"
        self.open_orders: list[object] = []
        self.status = "TRADING"
        self.market_step = "0.001"
        self.min_notional = "5"

    def request(self, method: str, path: str, params: dict[str, str]):
        self.calls.append((method, path, params))
        symbol = params.get("symbol", "ETHUSDC")
        if path == "/api/v3/exchangeInfo":
            return {
                "symbols": [
                    {
                        "symbol": symbol,
                        "baseAsset": symbol.removesuffix("USDC"),
                        "quoteAsset": "USDC",
                        "status": self.status,
                        "isSpotTradingAllowed": True,
                        "orderTypes": ["MARKET"],
                        "quoteOrderQtyMarketAllowed": True,
                        "filters": [
                            {
                                "filterType": "LOT_SIZE",
                                "minQty": "0.001",
                                "maxQty": "1000",
                                "stepSize": self.market_step,
                            },
                            {
                                "filterType": "MARKET_LOT_SIZE",
                                "minQty": "0.001",
                                "maxQty": "1000",
                                "stepSize": self.market_step,
                            },
                            {"filterType": "MIN_NOTIONAL", "minNotional": self.min_notional},
                        ],
                    }
                ]
            }
        if path == "/api/v3/ticker/bookTicker":
            return {"symbol": symbol, "bidPrice": self.bid, "askPrice": self.ask}
        if path == "/api/v3/account":
            return {
                "canTrade": True,
                "accountType": "SPOT",
                "balances": [
                    {"asset": "USDC", "free": self.free_usdc, "locked": "0"},
                    {"asset": symbol.removesuffix("USDC"), "free": self.free_base, "locked": "0"},
                ],
            }
        if path == "/api/v3/openOrders":
            return self.open_orders
        raise AssertionError(path)


def buy(reference: str = "100") -> TrialIntent:
    return TrialIntent(
        "trial-entry",
        "account",
        "ETHUSDC",
        "BUY",
        "strategy",
        D(reference),
        quote_budget=D("50"),
    )


def sell(quantity: str = "0.500", reference: str = "100") -> TrialIntent:
    return TrialIntent(
        "trial-exit",
        "account",
        "ETHUSDC",
        "SELL",
        "strategy",
        D(reference),
        base_quantity=D(quantity),
    )


def guard(transport: Transport) -> TrialPreSubmitGuard:
    return TrialPreSubmitGuard(transport, account_fingerprint="account")


def test_buy_requires_current_market_book_account_and_open_order_reads() -> None:
    transport = Transport()
    check = guard(transport)
    check.check(buy())
    assert [path for _, path, _ in transport.calls] == [
        "/api/v3/exchangeInfo",
        "/api/v3/ticker/bookTicker",
        "/api/v3/account",
        "/api/v3/openOrders",
    ]
    assert check(buy()) is True


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (lambda t: setattr(t, "status", "BREAK"), "MARKET_NOT_TRADABLE"),
        (lambda t: setattr(t, "free_usdc", "59.99"), "FREE_USDC_BELOW_60"),
        (lambda t: setattr(t, "open_orders", [{"orderId": 1}]), "OPEN_ORDERS_PRESENT"),
        (lambda t: setattr(t, "min_notional", "51"), "BUY_NOTIONAL_FILTER_BLOCKED"),
        (lambda t: setattr(t, "ask", "100.26"), "REFERENCE_DEVIATION_OVER_25_BPS"),
    ],
)
def test_buy_fails_closed_on_changed_exchange_state(mutation, reason: str) -> None:
    transport = Transport()
    mutation(transport)
    with pytest.raises(TrialSafetyError, match=reason):
        guard(transport).check(buy())


def test_exact_25_bps_boundary_is_allowed_but_more_is_not() -> None:
    transport = Transport()
    transport.ask = "100.25"
    guard(transport).check(buy())
    transport.ask = "100.2501"
    with pytest.raises(TrialSafetyError, match="REFERENCE_DEVIATION"):
        guard(transport).check(buy())


def test_sell_requires_free_owned_quantity_and_exact_current_steps() -> None:
    transport = Transport()
    guard(transport).check(sell("0.500"))
    transport.free_base = "0.499"
    with pytest.raises(TrialSafetyError, match="OWNED_BASE_NOT_FREE"):
        guard(transport).check(sell("0.500"))
    transport.free_base = "0.500"
    with pytest.raises(TrialSafetyError, match="LOT_SIZE"):
        guard(transport).check(sell("0.5005"))


def test_sell_notional_and_reference_price_are_checked_on_bid() -> None:
    transport = Transport()
    transport.bid = "9.99"
    transport.ask = "10.00"
    with pytest.raises(TrialSafetyError, match="SELL_NOTIONAL_FILTER_BLOCKED"):
        guard(transport).check(sell("0.500", reference="10"))
    transport.bid = "9.97"
    with pytest.raises(TrialSafetyError, match="REFERENCE_DEVIATION"):
        guard(transport).check(sell("1.000", reference="10"))


def test_wrong_account_or_quote_never_passes() -> None:
    transport = Transport()
    wrong_account = TrialIntent(
        "x", "other", "ETHUSDC", "BUY", "strategy", D("100"), quote_budget=D("50")
    )
    with pytest.raises(TrialSafetyError, match="ACCOUNT_FINGERPRINT"):
        guard(transport).check(wrong_account)
    with pytest.raises(ValueError, match="USDC-only"):
        TrialPreSubmitGuard(transport, account_fingerprint="account", quote_asset="USDT")


def test_callable_returns_false_without_exposing_provider_payload() -> None:
    transport = Transport()
    transport.ask = "1000"
    check = guard(transport)
    assert check(buy()) is False
    assert check.last_reason == "PRE_SUBMIT_BLOCKED"
