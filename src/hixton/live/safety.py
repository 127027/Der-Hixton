"""Immediate fail-closed safety checks for an explicitly armed one-shot order.

This module never establishes user consent and never submits an order.  It reads
current exchange/account state immediately before the existing executor is
allowed to claim a submit.  Any malformed, stale-looking or unexpected response
fails closed.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Protocol

from hixton.domain.markets import split_market
from hixton.live.orders import TrialIntent

_MAX_REFERENCE_DEVIATION_BPS = Decimal("25")
_MIN_TRIAL_FREE_QUOTE = Decimal("60")
_ZERO = Decimal(0)


class SafetyTransport(Protocol):
    def request(self, method: str, path: str, params: dict[str, str]) -> Any: ...


class TrialSafetyError(RuntimeError):
    """Fixed local safety reason; raw provider payloads are never embedded."""


class TrialPreSubmitGuard:
    """Validate the current exchange state immediately before one trial submit."""

    def __init__(
        self,
        transport: SafetyTransport,
        *,
        account_fingerprint: str,
        quote_asset: str = "USDC",
    ) -> None:
        if not account_fingerprint:
            raise ValueError("Explicit account fingerprint required")
        if quote_asset != "USDC":
            raise ValueError("The active one-shot release is USDC-only")
        self.transport = transport
        self.account_fingerprint = account_fingerprint
        self.quote_asset = quote_asset
        self.last_reason: str | None = None

    @staticmethod
    def _decimal(value: object, label: str) -> Decimal:
        if not isinstance(value, str):
            raise TrialSafetyError(f"{label}: decimal string missing")
        try:
            parsed = Decimal(value)
        except InvalidOperation:
            raise TrialSafetyError(f"{label}: invalid decimal") from None
        if not parsed.is_finite() or parsed < 0:
            raise TrialSafetyError(f"{label}: invalid amount")
        return parsed

    @staticmethod
    def _filter_map(market: dict[str, Any]) -> dict[str, dict[str, Any]]:
        filters = market.get("filters")
        if not isinstance(filters, list):
            raise TrialSafetyError("MARKET_FILTERS_MISSING")
        result: dict[str, dict[str, Any]] = {}
        for item in filters:
            if not isinstance(item, dict) or not isinstance(item.get("filterType"), str):
                raise TrialSafetyError("MARKET_FILTERS_INVALID")
            kind = item["filterType"]
            if kind in result:
                raise TrialSafetyError("MARKET_FILTER_DUPLICATE")
            result[kind] = item
        return result

    @staticmethod
    def _aligned(quantity: Decimal, rule: dict[str, Any]) -> bool:
        minimum = TrialPreSubmitGuard._decimal(rule.get("minQty"), "minQty")
        maximum = TrialPreSubmitGuard._decimal(rule.get("maxQty"), "maxQty")
        step = TrialPreSubmitGuard._decimal(rule.get("stepSize"), "stepSize")
        if quantity < minimum or (maximum > 0 and quantity > maximum):
            return False
        if step <= 0:
            return True
        return quantity % step == 0

    @staticmethod
    def _notional_allowed(notional: Decimal, filters: dict[str, dict[str, Any]]) -> bool:
        found = False
        minimum = filters.get("MIN_NOTIONAL")
        if minimum is not None:
            found = True
            if TrialPreSubmitGuard._decimal(minimum.get("minNotional"), "minNotional") > notional:
                return False
        bounded = filters.get("NOTIONAL")
        if bounded is not None:
            found = True
            if TrialPreSubmitGuard._decimal(bounded.get("minNotional"), "minNotional") > notional:
                return False
            maximum = TrialPreSubmitGuard._decimal(bounded.get("maxNotional"), "maxNotional")
            if maximum > 0 and notional > maximum:
                return False
        return found

    def _market(self, symbol: str) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
        payload = self.transport.request("GET", "/api/v3/exchangeInfo", {"symbol": symbol})
        if not isinstance(payload, dict) or not isinstance(payload.get("symbols"), list):
            raise TrialSafetyError("MARKET_RESPONSE_INVALID")
        rows = payload["symbols"]
        if len(rows) != 1 or not isinstance(rows[0], dict):
            raise TrialSafetyError("MARKET_IDENTITY_UNRESOLVED")
        market = rows[0]
        base, quote = split_market(symbol)
        if (
            market.get("symbol") != symbol
            or market.get("baseAsset") != base
            or market.get("quoteAsset") != quote
            or quote != self.quote_asset
            or market.get("status") != "TRADING"
            or market.get("isSpotTradingAllowed") is not True
            or "MARKET" not in market.get("orderTypes", [])
        ):
            raise TrialSafetyError("MARKET_NOT_TRADABLE")
        return market, self._filter_map(market)

    def _book_price(self, intent: TrialIntent) -> Decimal:
        payload = self.transport.request(
            "GET", "/api/v3/ticker/bookTicker", {"symbol": intent.symbol}
        )
        if not isinstance(payload, dict) or payload.get("symbol") != intent.symbol:
            raise TrialSafetyError("BOOK_IDENTITY_INVALID")
        bid = self._decimal(payload.get("bidPrice"), "bidPrice")
        ask = self._decimal(payload.get("askPrice"), "askPrice")
        if bid <= 0 or ask <= 0 or bid > ask:
            raise TrialSafetyError("BOOK_PRICE_INVALID")
        executable = ask if intent.side == "BUY" else bid
        deviation = abs(executable / intent.reference_price - Decimal(1)) * Decimal(10_000)
        if deviation > _MAX_REFERENCE_DEVIATION_BPS:
            raise TrialSafetyError("REFERENCE_DEVIATION_OVER_25_BPS")
        return executable

    def _balances(self) -> dict[str, tuple[Decimal, Decimal]]:
        account = self.transport.request("GET", "/api/v3/account", {"omitZeroBalances": "true"})
        if not isinstance(account, dict) or account.get("canTrade") is not True:
            raise TrialSafetyError("ACCOUNT_NOT_TRADABLE")
        if account.get("accountType") != "SPOT" or not isinstance(account.get("balances"), list):
            raise TrialSafetyError("ACCOUNT_NOT_SPOT")
        balances: dict[str, tuple[Decimal, Decimal]] = {}
        for row in account["balances"]:
            if not isinstance(row, dict) or not isinstance(row.get("asset"), str):
                raise TrialSafetyError("BALANCE_ROW_INVALID")
            asset = row["asset"]
            if asset in balances:
                raise TrialSafetyError("BALANCE_ROW_DUPLICATE")
            balances[asset] = (
                self._decimal(row.get("free"), f"{asset}.free"),
                self._decimal(row.get("locked"), f"{asset}.locked"),
            )
        if any(locked > 0 for _, locked in balances.values()):
            raise TrialSafetyError("LOCKED_BALANCE_PRESENT")
        return balances

    def check(self, intent: TrialIntent) -> None:
        if intent.account_fingerprint != self.account_fingerprint:
            raise TrialSafetyError("ACCOUNT_FINGERPRINT_MISMATCH")
        base, quote = split_market(intent.symbol)
        if quote != self.quote_asset:
            raise TrialSafetyError("NON_USDC_INTENT")

        market, filters = self._market(intent.symbol)
        if not {"LOT_SIZE", "MARKET_LOT_SIZE"} <= filters.keys():
            raise TrialSafetyError("QUANTITY_FILTERS_INCOMPLETE")
        price = self._book_price(intent)
        balances = self._balances()
        open_orders = self.transport.request("GET", "/api/v3/openOrders", {})
        if not isinstance(open_orders, list) or open_orders:
            raise TrialSafetyError("OPEN_ORDERS_PRESENT")

        if intent.side == "BUY":
            if market.get("quoteOrderQtyMarketAllowed") is not True:
                raise TrialSafetyError("QUOTE_ORDER_QTY_NOT_ALLOWED")
            if intent.quote_budget != Decimal("50") or intent.base_quantity != _ZERO:
                raise TrialSafetyError("BUY_BUDGET_NOT_EXACT_50")
            free_quote = balances.get(self.quote_asset, (_ZERO, _ZERO))[0]
            if free_quote < _MIN_TRIAL_FREE_QUOTE:
                raise TrialSafetyError("FREE_USDC_BELOW_60")
            if not self._notional_allowed(intent.quote_budget, filters):
                raise TrialSafetyError("BUY_NOTIONAL_FILTER_BLOCKED")
            # quoteOrderQty lets Binance derive the exact base quantity. We still
            # require both quantity-filter families to exist, but never invent a
            # rounded base quantity before the exchange executes the Market BUY.
        else:
            if intent.quote_budget != _ZERO or intent.base_quantity <= _ZERO:
                raise TrialSafetyError("SELL_QUANTITY_INVALID")
            free_base = balances.get(base, (_ZERO, _ZERO))[0]
            if free_base < intent.base_quantity:
                raise TrialSafetyError("OWNED_BASE_NOT_FREE")
            if not self._aligned(intent.base_quantity, filters["LOT_SIZE"]):
                raise TrialSafetyError("SELL_LOT_SIZE_BLOCKED")
            if not self._aligned(intent.base_quantity, filters["MARKET_LOT_SIZE"]):
                raise TrialSafetyError("SELL_MARKET_LOT_SIZE_BLOCKED")
            if not self._notional_allowed(intent.base_quantity * price, filters):
                raise TrialSafetyError("SELL_NOTIONAL_FILTER_BLOCKED")

    def __call__(self, intent: TrialIntent) -> bool:
        try:
            self.check(intent)
        except (TrialSafetyError, ValueError, RuntimeError):
            self.last_reason = "PRE_SUBMIT_BLOCKED"
            return False
        self.last_reason = None
        return True
