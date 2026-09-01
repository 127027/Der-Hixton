"""SQLite persistence for paper settings, account, checkpoints and audit events."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from types import TracebackType
from uuid import uuid4

from hixton.constants import SYMBOLS
from hixton.paper.models import (
    PaperAccount,
    PaperEvent,
    PaperEventStatus,
    PaperPosition,
    PaperSettings,
)


def _now() -> datetime:
    return datetime.now(UTC)


def _time(value: datetime) -> str:
    return value.astimezone(UTC).isoformat()


def _parse_time(value: object) -> datetime:
    return datetime.fromisoformat(str(value)).astimezone(UTC)


class PaperStore:
    """Short-lived SQLite connection; instantiate per worker or API request."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path, timeout=30)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._migrate()

    def __enter__(self) -> PaperStore:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is None:
            self._connection.commit()
        else:
            self._connection.rollback()
        self.close()

    def close(self) -> None:
        self._connection.close()

    def initialize(self, *, at: datetime | None = None) -> None:
        moment = (at or _now()).astimezone(UTC)
        with self._connection:
            self._connection.execute(
                """
                INSERT OR IGNORE INTO paper_account (
                    singleton, cash_text, starting_cash_text, high_water_text,
                    day_start_equity_text, day_start_date_utc, halted,
                    halt_reason, created_at_utc, updated_at_utc
                ) VALUES (1, '240.00', '240.00', '240.00', '240.00', ?, 0, NULL, ?, ?)
                """,
                (moment.date().isoformat(), _time(moment), _time(moment)),
            )
            self._connection.execute(
                """
                INSERT OR IGNORE INTO paper_settings (
                    singleton, slot_count, target_notional_text, emergency_stop, updated_at_utc
                ) VALUES (1, 3, '80.00', 0, ?)
                """,
                (_time(moment),),
            )

    def load_account(self) -> PaperAccount:
        row = self._connection.execute(
            "SELECT * FROM paper_account WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise RuntimeError("paper account is not initialized")
        return PaperAccount(
            cash_usdt=Decimal(str(row["cash_text"])),
            starting_cash_usdt=Decimal(str(row["starting_cash_text"])),
            high_water_equity_usdt=Decimal(str(row["high_water_text"])),
            day_start_equity_usdt=Decimal(str(row["day_start_equity_text"])),
            day_start_date_utc=str(row["day_start_date_utc"]),
            halted=bool(row["halted"]),
            halt_reason=str(row["halt_reason"]) if row["halt_reason"] is not None else None,
            created_at_utc=_parse_time(row["created_at_utc"]),
            updated_at_utc=_parse_time(row["updated_at_utc"]),
        )

    def save_account(self, account: PaperAccount) -> None:
        with self._connection:
            self._connection.execute(
                """
                UPDATE paper_account SET
                    cash_text=?, starting_cash_text=?, high_water_text=?,
                    day_start_equity_text=?, day_start_date_utc=?, halted=?,
                    halt_reason=?, updated_at_utc=?
                WHERE singleton=1
                """,
                (
                    str(account.cash_usdt),
                    str(account.starting_cash_usdt),
                    str(account.high_water_equity_usdt),
                    str(account.day_start_equity_usdt),
                    account.day_start_date_utc,
                    int(account.halted),
                    account.halt_reason,
                    _time(account.updated_at_utc),
                ),
            )

    def load_settings(self) -> PaperSettings:
        row = self._connection.execute(
            "SELECT * FROM paper_settings WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise RuntimeError("paper settings are not initialized")
        return PaperSettings(
            slot_count=int(row["slot_count"]),
            target_notional_usdt=Decimal(str(row["target_notional_text"])),
            emergency_stop=bool(row["emergency_stop"]),
        )

    def save_settings(self, settings: PaperSettings, *, at: datetime | None = None) -> None:
        moment = (at or _now()).astimezone(UTC)
        previous = self.load_settings()
        with self._connection:
            self._connection.execute(
                """
                UPDATE paper_settings SET slot_count=?, target_notional_text=?,
                    emergency_stop=?, updated_at_utc=?
                WHERE singleton=1
                """,
                (
                    settings.slot_count,
                    str(settings.target_notional_usdt),
                    int(settings.emergency_stop),
                    _time(moment),
                ),
            )
            self._connection.execute(
                """
                INSERT INTO paper_audit(
                    audit_id, occurred_at_utc, actor, action, details_json
                ) VALUES (?, ?, 'LOCAL_UI', 'PAPER_SETTINGS_CHANGED', ?)
                """,
                (
                    str(uuid4()),
                    _time(moment),
                    json.dumps(
                        {
                            "before": {
                                "slot_count": previous.slot_count,
                                "target_notional_usdt": str(previous.target_notional_usdt),
                                "emergency_stop": previous.emergency_stop,
                            },
                            "after": {
                                "slot_count": settings.slot_count,
                                "target_notional_usdt": str(settings.target_notional_usdt),
                                "emergency_stop": settings.emergency_stop,
                            },
                            "scope": "future_entries_only",
                        },
                        separators=(",", ":"),
                    ),
                ),
            )

    def load_positions(self) -> tuple[PaperPosition, ...]:
        rows = self._connection.execute(
            "SELECT * FROM paper_positions ORDER BY symbol"
        ).fetchall()
        return tuple(
            PaperPosition(
                symbol=str(row["symbol"]),
                quantity=Decimal(str(row["quantity_text"])),
                average_price=Decimal(str(row["average_price_text"])),
                cost_basis_usdt=Decimal(str(row["cost_basis_text"])),
                entry_time_utc=_parse_time(row["entry_time_utc"]),
                entry_signal_id=str(row["entry_signal_id"]),
                entry_fee_usdt=Decimal(str(row["entry_fee_text"])),
                updated_at_utc=_parse_time(row["updated_at_utc"]),
            )
            for row in rows
        )

    def upsert_position(self, position: PaperPosition) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO paper_positions (
                    symbol, quantity_text, average_price_text, cost_basis_text,
                    entry_time_utc, entry_signal_id, entry_fee_text, updated_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET
                    quantity_text=excluded.quantity_text,
                    average_price_text=excluded.average_price_text,
                    cost_basis_text=excluded.cost_basis_text,
                    entry_time_utc=excluded.entry_time_utc,
                    entry_signal_id=excluded.entry_signal_id,
                    entry_fee_text=excluded.entry_fee_text,
                    updated_at_utc=excluded.updated_at_utc
                """,
                (
                    position.symbol,
                    str(position.quantity),
                    str(position.average_price),
                    str(position.cost_basis_usdt),
                    _time(position.entry_time_utc),
                    position.entry_signal_id,
                    str(position.entry_fee_usdt),
                    _time(position.updated_at_utc),
                ),
            )

    def delete_position(self, symbol: str) -> None:
        with self._connection:
            self._connection.execute(
                "DELETE FROM paper_positions WHERE symbol=?",
                (symbol.replace("/", "").upper(),),
            )

    def append_event(self, event: PaperEvent) -> bool:
        with self._connection:
            cursor = self._connection.execute(
                """
                INSERT OR IGNORE INTO paper_events (
                    event_id, signal_id, occurred_at_utc, symbol, action, status,
                    reason, reference_price_text, execution_price_text,
                    base_quantity_text, quote_amount_text, fee_text,
                    realized_pnl_text, breakout_strength_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.signal_id,
                    _time(event.occurred_at_utc),
                    event.symbol,
                    event.action,
                    event.status.value,
                    event.reason,
                    str(event.reference_price),
                    str(event.execution_price) if event.execution_price is not None else None,
                    str(event.base_quantity) if event.base_quantity is not None else None,
                    str(event.quote_amount_usdt) if event.quote_amount_usdt is not None else None,
                    str(event.fee_usdt) if event.fee_usdt is not None else None,
                    (
                        str(event.realized_pnl_usdt)
                        if event.realized_pnl_usdt is not None
                        else None
                    ),
                    (
                        str(event.breakout_strength)
                        if event.breakout_strength is not None
                        else None
                    ),
                ),
            )
        return cursor.rowcount == 1

    def apply_cycle(
        self,
        *,
        account: PaperAccount,
        positions: Mapping[str, PaperPosition],
        events: tuple[PaperEvent, ...],
        checkpoints: Mapping[str, datetime],
    ) -> None:
        """Atomically persist one deterministic bar-close processing cycle."""

        with self._connection:
            self._connection.execute(
                """
                UPDATE paper_account SET
                    cash_text=?, starting_cash_text=?, high_water_text=?,
                    day_start_equity_text=?, day_start_date_utc=?, halted=?,
                    halt_reason=?, updated_at_utc=?
                WHERE singleton=1
                """,
                (
                    str(account.cash_usdt),
                    str(account.starting_cash_usdt),
                    str(account.high_water_equity_usdt),
                    str(account.day_start_equity_usdt),
                    account.day_start_date_utc,
                    int(account.halted),
                    account.halt_reason,
                    _time(account.updated_at_utc),
                ),
            )
            self._connection.execute("DELETE FROM paper_positions")
            self._connection.executemany(
                """
                INSERT INTO paper_positions (
                    symbol, quantity_text, average_price_text, cost_basis_text,
                    entry_time_utc, entry_signal_id, entry_fee_text, updated_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        position.symbol,
                        str(position.quantity),
                        str(position.average_price),
                        str(position.cost_basis_usdt),
                        _time(position.entry_time_utc),
                        position.entry_signal_id,
                        str(position.entry_fee_usdt),
                        _time(position.updated_at_utc),
                    )
                    for position in positions.values()
                ],
            )
            self._connection.executemany(
                """
                INSERT OR IGNORE INTO paper_events (
                    event_id, signal_id, occurred_at_utc, symbol, action, status,
                    reason, reference_price_text, execution_price_text,
                    base_quantity_text, quote_amount_text, fee_text,
                    realized_pnl_text, breakout_strength_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        event.event_id,
                        event.signal_id,
                        _time(event.occurred_at_utc),
                        event.symbol,
                        event.action,
                        event.status.value,
                        event.reason,
                        str(event.reference_price),
                        (
                            str(event.execution_price)
                            if event.execution_price is not None
                            else None
                        ),
                        str(event.base_quantity) if event.base_quantity is not None else None,
                        (
                            str(event.quote_amount_usdt)
                            if event.quote_amount_usdt is not None
                            else None
                        ),
                        str(event.fee_usdt) if event.fee_usdt is not None else None,
                        (
                            str(event.realized_pnl_usdt)
                            if event.realized_pnl_usdt is not None
                            else None
                        ),
                        (
                            str(event.breakout_strength)
                            if event.breakout_strength is not None
                            else None
                        ),
                    )
                    for event in events
                ],
            )
            self._connection.executemany(
                """
                INSERT INTO paper_checkpoints(symbol, last_close_utc) VALUES (?, ?)
                ON CONFLICT(symbol) DO UPDATE SET last_close_utc=excluded.last_close_utc
                """,
                [(symbol, _time(value)) for symbol, value in checkpoints.items()],
            )

    def load_events(
        self,
        *,
        symbol: str | None = None,
        limit: int = 500,
    ) -> tuple[PaperEvent, ...]:
        if limit <= 0 or limit > 5_000:
            raise ValueError("paper event limit must be between 1 and 5000")
        parameters: list[object] = []
        clause = ""
        if symbol is not None:
            clause = "WHERE symbol=?"
            parameters.append(symbol.replace("/", "").upper())
        parameters.append(limit)
        rows = self._connection.execute(
            f"SELECT * FROM paper_events {clause} ORDER BY occurred_at_utc DESC LIMIT ?",
            parameters,
        ).fetchall()
        return tuple(self._row_to_event(row) for row in rows)

    def checkpoint(self, symbol: str) -> datetime | None:
        row = self._connection.execute(
            "SELECT last_close_utc FROM paper_checkpoints WHERE symbol=?",
            (symbol.replace("/", "").upper(),),
        ).fetchone()
        return _parse_time(row["last_close_utc"]) if row is not None else None

    def save_checkpoints(self, values: Mapping[str, datetime]) -> None:
        with self._connection:
            self._connection.executemany(
                """
                INSERT INTO paper_checkpoints(symbol, last_close_utc) VALUES (?, ?)
                ON CONFLICT(symbol) DO UPDATE SET last_close_utc=excluded.last_close_utc
                """,
                [
                    (symbol.replace("/", "").upper(), _time(value))
                    for symbol, value in values.items()
                ],
            )

    def all_checkpoints(self) -> dict[str, datetime]:
        rows = self._connection.execute(
            "SELECT symbol, last_close_utc FROM paper_checkpoints"
        ).fetchall()
        return {str(row["symbol"]): _parse_time(row["last_close_utc"]) for row in rows}

    def _migrate(self) -> None:
        with self._connection:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS paper_account (
                    singleton INTEGER PRIMARY KEY CHECK (singleton=1),
                    cash_text TEXT NOT NULL,
                    starting_cash_text TEXT NOT NULL,
                    high_water_text TEXT NOT NULL,
                    day_start_equity_text TEXT NOT NULL,
                    day_start_date_utc TEXT NOT NULL,
                    halted INTEGER NOT NULL CHECK (halted IN (0, 1)),
                    halt_reason TEXT,
                    created_at_utc TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS paper_settings (
                    singleton INTEGER PRIMARY KEY CHECK (singleton=1),
                    slot_count INTEGER NOT NULL CHECK (slot_count > 0),
                    target_notional_text TEXT NOT NULL,
                    emergency_stop INTEGER NOT NULL CHECK (emergency_stop IN (0, 1)),
                    updated_at_utc TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS paper_positions (
                    symbol TEXT PRIMARY KEY,
                    quantity_text TEXT NOT NULL,
                    average_price_text TEXT NOT NULL,
                    cost_basis_text TEXT NOT NULL,
                    entry_time_utc TEXT NOT NULL,
                    entry_signal_id TEXT NOT NULL,
                    entry_fee_text TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS paper_events (
                    event_id TEXT PRIMARY KEY,
                    signal_id TEXT NOT NULL UNIQUE,
                    occurred_at_utc TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    reason TEXT,
                    reference_price_text TEXT NOT NULL,
                    execution_price_text TEXT,
                    base_quantity_text TEXT,
                    quote_amount_text TEXT,
                    fee_text TEXT,
                    realized_pnl_text TEXT,
                    breakout_strength_text TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_paper_events_symbol_time
                ON paper_events(symbol, occurred_at_utc);
                CREATE INDEX IF NOT EXISTS idx_paper_events_time
                ON paper_events(occurred_at_utc);
                CREATE TABLE IF NOT EXISTS paper_checkpoints (
                    symbol TEXT PRIMARY KEY,
                    last_close_utc TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS paper_audit (
                    audit_id TEXT PRIMARY KEY,
                    occurred_at_utc TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_paper_audit_time
                ON paper_audit(occurred_at_utc);
                """
            )
            columns = {
                str(row["name"])
                for row in self._connection.execute("PRAGMA table_info(paper_events)").fetchall()
            }
            if "realized_pnl_text" not in columns:
                self._connection.execute(
                    "ALTER TABLE paper_events ADD COLUMN realized_pnl_text TEXT"
                )
            self._connection.execute("PRAGMA optimize")

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> PaperEvent:
        def decimal_or_none(name: str) -> Decimal | None:
            value = row[name]
            return Decimal(str(value)) if value is not None else None

        return PaperEvent(
            event_id=str(row["event_id"]),
            signal_id=str(row["signal_id"]),
            occurred_at_utc=_parse_time(row["occurred_at_utc"]),
            symbol=str(row["symbol"]),
            action=str(row["action"]),
            status=PaperEventStatus(str(row["status"])),
            reason=str(row["reason"]) if row["reason"] is not None else None,
            reference_price=Decimal(str(row["reference_price_text"])),
            execution_price=decimal_or_none("execution_price_text"),
            base_quantity=decimal_or_none("base_quantity_text"),
            quote_amount_usdt=decimal_or_none("quote_amount_text"),
            fee_usdt=decimal_or_none("fee_text"),
            realized_pnl_usdt=decimal_or_none("realized_pnl_text"),
            breakout_strength=decimal_or_none("breakout_strength_text"),
        )

    def missing_checkpoint_symbols(self) -> tuple[str, ...]:
        present = set(self.all_checkpoints())
        return tuple(symbol for symbol in SYMBOLS if symbol not in present)
