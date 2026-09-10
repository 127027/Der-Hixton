"""Audited preparation and fail-closed one-shot runtime wiring."""

from __future__ import annotations

import json
import sqlite3
import time
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from functools import partial
from pathlib import Path
from threading import RLock
from uuid import uuid4

from hixton.constants import SYMBOLS
from hixton.domain.versions import StrategyDefinition
from hixton.live.binance import BinanceCheckError, BinanceReadOnlyClient, assess_account
from hixton.live.credentials import BinanceCredentials, CredentialService, LocalAccess, Vault
from hixton.live.exchange import BinanceSpotExchange, BinanceSpotTransport
from hixton.live.orders import ExchangeOrder, OrderJournal, TrialIntent, TrialOrderExecutor
from hixton.live.reconciliation import AccountSnapshot, TrialReconciler, read_account_snapshot
from hixton.live.runtime import TrialRuntime
from hixton.live.safety import TrialPreSubmitGuard
from hixton.live.trial import SignalTrial

_PRODUCTION = "https://api.binance.com"
_TESTNET = "https://testnet.binance.vision"
RELEASE_BLOCKERS = (
    "USDC-Migration und Echtorder-Anschluss benötigen gemeinsame Betriebsabnahme; "
    "USDT-Signale werden nicht als USDC ausgeführt.",
    "Einmaltest-Laufzeit, Kontobaseline, 25-bp-Preischeck und frische Pre-Submit-Prüfung "
    "sind technisch vorbereitet; Restmengen/Fremdorder und externe Abnahme bleiben offen.",
    "Keine normale Livefreigabe für die aktive Strategie; Paper-Freigabe ist keine Echtgeldfreigabe.",
    "Binance-Testnet-/Störfallabnahme des Release Candidates fehlt.",
)
_USDC_CLIENT = partial(BinanceReadOnlyClient, quote_asset="USDC")


class LivePreparation:
    def __init__(
        self,
        database: Path,
        vault: Vault,
        client_factory: Callable[..., BinanceReadOnlyClient] = _USDC_CLIENT,
        *,
        order_base_url: str = _PRODUCTION,
    ) -> None:
        if order_base_url not in {_PRODUCTION, _TESTNET}:
            raise ValueError("Explicit Binance production or Spot-testnet trial host required")
        self.database = database
        self.credentials = CredentialService(vault)
        self.access = LocalAccess(vault)
        self.lock = RLock()
        self.client_factory = client_factory
        self.order_base_url = order_base_url
        self._check: dict[str, object] | None = None
        self._check_time = 0.0
        self._check_fingerprint: str | None = None
        self._next_check = 0.0
        self.trial: SignalTrial | None = None
        self.runtime: TrialRuntime | None = None
        self.reconciler: TrialReconciler | None = None
        self.snapshot_reader: Callable[[], AccountSnapshot] | None = None
        self._pre_submit_connected = False

    @property
    def environment(self) -> str:
        return "TESTNET" if self.order_base_url == _TESTNET else "PRODUCTION"

    def connect_runtime(self, strategy: StrategyDefinition) -> TrialRuntime:
        """Wire durable recovery without granting a public BUY action at startup."""
        service = self

        def bound_exchange() -> BinanceSpotExchange:
            credentials = service.credentials.load()
            if credentials is None:
                raise BinanceCheckError("Binance-Schlüssel fehlt")
            transport = BinanceSpotTransport(credentials, base_url=service.order_base_url)
            return BinanceSpotExchange(
                transport, account_fingerprint=credentials.fingerprint, quote_asset="USDC"
            )

        class DeferredExchange:
            def submit(self, intent: TrialIntent) -> ExchangeOrder:
                return bound_exchange().submit(intent)

            def query(self, intent: TrialIntent) -> ExchangeOrder | None:
                return bound_exchange().query(intent)

        def pre_submit(intent: TrialIntent) -> bool:
            try:
                exchange = bound_exchange()
                guard = TrialPreSubmitGuard(
                    exchange.transport,
                    account_fingerprint=exchange.account_fingerprint,
                    quote_asset="USDC",
                )
                allowed = guard(intent)
            except Exception:
                allowed = False
            service.audit(
                "TRIAL_PRE_SUBMIT_ALLOWED" if allowed else "TRIAL_PRE_SUBMIT_BLOCKED",
                {
                    "intent_id": intent.intent_id,
                    "symbol": intent.symbol,
                    "side": intent.side,
                    "environment": service.environment,
                },
            )
            return allowed

        def snapshot() -> AccountSnapshot:
            exchange = bound_exchange()
            return read_account_snapshot(exchange.transport, account=exchange.account_fingerprint)

        journal = OrderJournal(self.database)
        self.reconciler = TrialReconciler(journal)
        self.snapshot_reader = snapshot
        self._pre_submit_connected = True
        self.trial = SignalTrial(
            journal,
            TrialOrderExecutor(journal, DeferredExchange(), pre_submit),
            strategy,
            self.technical_release_ready,
        )
        self.runtime = TrialRuntime(self.trial, self.reconciler, snapshot)
        return self.runtime

    def _fresh_check(self) -> dict[str, object] | None:
        if time.monotonic() - self._check_time > 60:
            return None
        return self._check

    def technical_release_ready(self) -> bool:
        """Technical entry gate only; public/manual consent remains a separate route gate."""
        try:
            credentials = self.credentials.load()
        except Exception:
            return False
        check = self._fresh_check()
        return bool(
            credentials is not None
            and self._check_fingerprint == credentials.fingerprint
            and check is not None
            and check.get("account_checks_passed") is True
            and self._pre_submit_connected
            and self.reconciler is not None
            and self.snapshot_reader is not None
            and (self.runtime is None or self.runtime.last_error is None)
        )

    def _discard_unused_baseline(self) -> None:
        """Rollback only a baseline that never became attached to a trial/intent."""
        if self.reconciler is None:
            return
        with self.reconciler.journal._connect() as connection:
            has_trial = connection.execute("SELECT 1 FROM signal_trial LIMIT 1").fetchone()
            has_intent = connection.execute("SELECT 1 FROM trial_intents LIMIT 1").fetchone()
            if not has_trial and not has_intent:
                connection.execute("DELETE FROM trial_account_baseline")
                self.reconciler.journal._audit(connection, "ACCOUNT", "UNUSED_BASELINE_ROLLED_BACK")

    def arm_trial(self, *, notional: Decimal) -> dict[str, object]:
        """Prepare exactly one durable entitlement after a fresh read-only account check.

        This method itself never submits an order. The public production HTTP route
        remains blocked until external Testnet/failure acceptance is recorded.
        """
        with self.lock:
            if not notional.is_finite() or notional != Decimal("50"):
                raise BinanceCheckError("Einmaltest benötigt genau 50 USDC.")
            if self.trial is None or self.reconciler is None or self.snapshot_reader is None:
                raise BinanceCheckError("Einmaltest-Laufzeit ist nicht vollständig verbunden.")
            if self.trial.report()["state"] != "NOT_STARTED":
                raise BinanceCheckError("Einmaltest wurde bereits angelegt; zuerst Zustand klären.")
            if not self.technical_release_ready():
                raise BinanceCheckError(
                    "Frische bestandene Binance-Kontoprüfung und technische Freigaben fehlen."
                )
            credentials = self.credentials.load()
            if credentials is None:
                raise BinanceCheckError("Binance-Schlüssel fehlt.")
            now = datetime.now(UTC)
            snapshot = self.snapshot_reader()
            try:
                self.reconciler.capture(snapshot, now=now)
                self.trial.arm(
                    str(uuid4()),
                    credentials.fingerprint,
                    now=now,
                    notional=notional,
                )
            except Exception:
                self._discard_unused_baseline()
                self.audit("TRIAL_ARM_FAILED", {"environment": self.environment})
                raise
            report = self.trial.report()
            self.audit(
                "TRIAL_ARMED",
                {
                    "trial_id": report.get("trial_id"),
                    "quote_asset": "USDC",
                    "notional": "50",
                    "environment": self.environment,
                },
            )
            return report

    def require_settled_for_key_change(self) -> None:
        if self.trial is not None and self.trial.report()["has_unsettled"]:
            raise BinanceCheckError(
                "Laufender/ungeklärter Einmaltest: Schlüssel nicht entfernen oder ersetzen. "
                "Zuerst Orders und Bestände vollständig abgleichen."
            )

    def execution_state(self) -> str:
        if self.runtime is not None and self.runtime.last_error:
            return "TRIAL_NEEDS_REVIEW"
        if self.trial is None:
            return "LIVE_DISABLED"
        report = self.trial.report()
        return "TRIAL_" + str(report["state"]) if report["has_unsettled"] else "LIVE_DISABLED"

    def stop_entries(self) -> dict[str, object]:
        with self.lock:
            if self.trial is not None:
                self.trial.disable_entries()
                report = self.trial.report()
            else:
                report = {"state": "NOT_STARTED", "has_unsettled": False}
            self.audit("LIVE_NEW_ENTRIES_DISABLED")
            return {
                "state": "EXIT_ONLY" if report["has_unsettled"] else "LIVE_DISABLED",
                "trial": report,
                "message": "Neue Echtgeld-Einstiege gesperrt; keine Position automatisch "
                "verkauft und keine Order blind storniert. Paper bleibt unverändert. "
                "Bei offenen/unklaren echten Beständen bleibt deren Betreuung erforderlich.",
            }

    def audit(self, action: str, details: dict[str, object] | None = None) -> None:
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database, timeout=10) as connection:
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS live_preparation_audit ("
                "id INTEGER PRIMARY KEY, at_utc TEXT NOT NULL, action TEXT NOT NULL, "
                "details_json TEXT NOT NULL)"
            )
            connection.execute(
                "INSERT INTO live_preparation_audit(at_utc, action, details_json) VALUES (?, ?, ?)",
                (datetime.now(UTC).isoformat(), action, json.dumps(details or {})),
            )

    def invalidate_check(self) -> None:
        self._check = None
        self._check_time = 0
        self._check_fingerprint = None

    @staticmethod
    def _testnet_permissions() -> dict[str, bool]:
        values = {
            "enableReading": True,
            "enableSpotAndMarginTrading": True,
            "ipRestrict": True,
            "enableWithdrawals": False,
            "enableMargin": False,
            "enableFutures": False,
            "enableInternalTransfer": False,
            "permitsUniversalTransfer": False,
            "enableVanillaOptions": False,
            "enablePortfolioMarginTrading": False,
            "enableFixApiTrade": False,
        }
        return values

    def _inspect_testnet(self, credentials: BinanceCredentials) -> dict[str, object]:
        """Spot-testnet readiness without pretending production SAPI permission proof."""
        transport = BinanceSpotTransport(credentials, base_url=_TESTNET)
        account = transport.request("GET", "/api/v3/account", {"omitZeroBalances": "true"})
        orders = transport.request("GET", "/api/v3/openOrders", {})
        markets = transport.request(
            "GET",
            "/api/v3/exchangeInfo",
            {"symbols": json.dumps(SYMBOLS, separators=(",", ":"))},
        )
        result = assess_account(
            self._testnet_permissions(),
            account,
            orders,
            markets,
            Decimal("50"),
            quote_asset="USDC",
        )
        result["environment"] = "TESTNET"
        result["production_api_permissions_verified"] = False
        result["note"] = (
            "Spot-Testnet Vorprüfung; Testnet-Guthaben ist kein Echtgeld und ersetzt keine "
            "Produktions-Key-/IP-Prüfung."
        )
        return result

    def check(self) -> dict[str, object]:
        with self.lock:
            if time.monotonic() < self._next_check:
                raise BinanceCheckError(
                    "Binance-Prüfung pausiert. Bitte nach der Wartezeit erneut prüfen."
                )
            credentials = self.credentials.load()
            if credentials is None:
                raise BinanceCheckError(
                    "Binance API-Schlüssel fehlt. Bitte lokal sicher eintragen."
                )
            self.invalidate_check()
            self._next_check = time.monotonic() + 30
            self.audit("BINANCE_READ_ONLY_CHECK_REQUESTED", {"environment": self.environment})
            try:
                if self.order_base_url == _TESTNET:
                    result = self._inspect_testnet(credentials)
                else:
                    result = self.client_factory(credentials).inspect(Decimal("50"))
                    result["environment"] = "PRODUCTION"
                    result["production_api_permissions_verified"] = True
            except BinanceCheckError as error:
                self._next_check = max(self._next_check, time.monotonic() + error.retry_after)
                self.audit("BINANCE_READ_ONLY_CHECK_FAILED", {"environment": self.environment})
                raise
            except Exception:
                self.audit("BINANCE_READ_ONLY_CHECK_FAILED", {"environment": self.environment})
                raise BinanceCheckError("Binance-Testnet-Prüfung fehlgeschlagen.") from None
            self._check = {**result, "checked_at_utc": datetime.now(UTC).isoformat()}
            self._check_time = time.monotonic()
            self._check_fingerprint = credentials.fingerprint
            self.audit(
                "BINANCE_READ_ONLY_CHECK_COMPLETE",
                {
                    "passed": result.get("account_checks_passed") is True,
                    "fingerprint": credentials.fingerprint,
                    "environment": self.environment,
                },
            )
            return dict(self._check)

    def status(self, *, authenticated: bool, soak_ready: bool, healthy: bool) -> dict[str, object]:
        with self.lock:
            credential_status = self.credentials.status()
            blockers = list(RELEASE_BLOCKERS)
            if self.runtime is not None and self.runtime.last_error:
                blockers.append(
                    "Einmaltest-Laufzeit/Abgleich benötigt Klärung; System & Logs prüfen."
                )
            if not credential_status["configured"]:
                blockers.insert(0, "Binance API-Schlüssel fehlt. Bitte hier lokal eintragen.")
            if not soak_ready:
                blockers.append(
                    "Paper-Dauertest noch nicht bestanden (mindestens 30 Tage / 20 Trades)."
                )
            if not healthy:
                blockers.append("Marktdaten/Bot derzeit nicht vollständig gesund.")
            fresh_check = self._fresh_check()
            if fresh_check is None:
                blockers.append("Keine frische Binance-Kontoprüfung (höchstens 60 Sekunden alt).")
            elif fresh_check.get("account_checks_passed") is not True:
                blockers.append("Binance-Kontoprüfung enthält Blockierungen.")
            return {
                "state": self.execution_state(),
                "order_dispatch_available": False,
                "ready": False,
                "authenticated": authenticated,
                "password_configured": self.access.configured(),
                "credentials": credential_status
                if authenticated
                else {"configured": credential_status["configured"]},
                "blockers": blockers,
                "account_check": fresh_check if authenticated else None,
                "trial_dispatch_available": False,
                "trial_quote_asset": "USDC",
                "trial_environment": self.environment,
                "trial_readiness": {
                    "quote_aware_order_adapter_offline_tested": True,
                    "runtime_connected": self.runtime is not None,
                    "balance_conservation_connected": self.runtime is not None,
                    "fresh_pre_submit_guard_connected": self._pre_submit_connected,
                    "baseline_arm_path_connected": self.reconciler is not None,
                    "technical_release_ready": self.technical_release_ready(),
                    "production_submission_accepted": False,
                    "account_reconciliation_accepted": False,
                    "binance_testnet_accepted": False,
                },
                "trial": self.trial.report()
                if authenticated and self.trial is not None
                else {"state": "NOT_STARTED" if self.trial is None else "LOCKED"},
                "first_live_trial": {
                    "slot_count": 1,
                    "quote_asset": "USDC",
                    "target_notional_quote": "50.00",
                    "minimum_free_quote": "60.00",
                    "max_reference_deviation_bps": "25",
                },
            }
