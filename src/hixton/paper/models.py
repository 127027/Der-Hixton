"""Immutable paper-ledger records and runtime settings."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from hixton.constants import HIXTON_SPEC_VERSION


class PaperEventStatus(StrEnum):
    FILLED = "FILLED"
    BLOCKED = "BLOCKED"
    OBSERVED = "OBSERVED"


@dataclass(frozen=True, slots=True)
class PaperSettings:
    slot_count: int = 3
    target_notional_usdt: Decimal = Decimal("80.00")
    emergency_stop: bool = False

    def __post_init__(self) -> None:
        if self.slot_count <= 0:
            raise ValueError("paper slot_count must be positive")
        if self.target_notional_usdt <= 0:
            raise ValueError("paper target_notional_usdt must be positive")
        if Decimal(self.slot_count) * self.target_notional_usdt > Decimal("240.00"):
            raise ValueError("slot_count multiplied by target notional may not exceed 240 USDT")


@dataclass(frozen=True, slots=True)
class PaperAccount:
    cash_usdt: Decimal
    starting_cash_usdt: Decimal
    high_water_equity_usdt: Decimal
    day_start_equity_usdt: Decimal
    day_start_date_utc: str
    halted: bool
    halt_reason: str | None
    created_at_utc: datetime
    updated_at_utc: datetime


@dataclass(frozen=True, slots=True)
class PaperPosition:
    symbol: str
    quantity: Decimal
    average_price: Decimal
    cost_basis_usdt: Decimal
    entry_time_utc: datetime
    entry_signal_id: str
    entry_fee_usdt: Decimal
    updated_at_utc: datetime
    strategy_version: str = HIXTON_SPEC_VERSION
    slot_count: int = 1


@dataclass(frozen=True, slots=True)
class PaperEvent:
    event_id: str
    signal_id: str
    occurred_at_utc: datetime
    symbol: str
    action: str
    status: PaperEventStatus
    reason: str | None
    reference_price: Decimal
    execution_price: Decimal | None
    base_quantity: Decimal | None
    quote_amount_usdt: Decimal | None
    fee_usdt: Decimal | None
    realized_pnl_usdt: Decimal | None
    breakout_strength: Decimal | None
    strategy_version: str = HIXTON_SPEC_VERSION
    processed_at_utc: datetime | None = None
    execution_model: str = "LEGACY_CLOSE_OR_MIGRATION"


@dataclass(frozen=True, slots=True)
class PaperStrategySession:
    strategy_key: str
    strategy_version: str
    activated_at_utc: datetime
    starting_equity_usdt: Decimal


@dataclass(frozen=True, slots=True)
class PaperPortfolio:
    account: PaperAccount
    settings: PaperSettings
    positions: tuple[PaperPosition, ...]
    equity_usdt: Decimal
    unrealized_pnl_usdt: Decimal
    daily_loss_paused: bool
    drawdown_pct: Decimal


@dataclass(frozen=True, slots=True)
class PaperSoakProgress:
    started_at_utc: datetime
    calendar_days: int
    processed_closed_bars_by_symbol: Mapping[str, int]
    minimum_processed_closed_bars: int
    completed_trades: int
    minimum_days: int
    minimum_closed_bars_per_symbol: int
    minimum_completed_trades: int
    maximum_days_when_trade_count_low: int
    status: str
    ready: bool
    blockers: tuple[str, ...]
