from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from hixton.live.credentials import BinanceCredentials
from hixton.live.reconciliation import AccountSnapshot
from tests.test_live_preparation import (
    HEADERS,
    MemoryVault,
    PASSWORD,
    client_for,
    save_key,
    unlock,
)


class PassingReadOnlyClient:
    def __init__(self, credentials: BinanceCredentials) -> None:
        self.credentials = credentials

    def inspect(self, notional: Decimal) -> dict[str, object]:
        assert notional == Decimal("50")
        return {
            "account_checks_passed": True,
            "blockers": [],
            "free_usdc": "100",
            "free_bnb": "0",
        }


def ready_service(tmp_path):
    client, config, service = client_for(tmp_path, MemoryVault())
    unlock(client)
    save_key(client)
    service.client_factory = PassingReadOnlyClient
    assert client.post("/api/live/check", headers=HEADERS, json={}).status_code == 200
    credentials = service.credentials.load()
    assert credentials is not None
    service.snapshot_reader = lambda: AccountSnapshot(
        credentials.fingerprint,
        datetime.now(UTC),
        {"USDC": (Decimal("100"), Decimal("0"))},
        (),
    )
    assert service.technical_release_ready() is True
    return client, config, service, credentials


def test_internal_arm_captures_baseline_and_waits_for_a_new_signal(tmp_path) -> None:
    _, config, service, credentials = ready_service(tmp_path)
    report = service.arm_trial(notional=Decimal("50"))
    assert report["state"] == "WAITING_SIGNAL"
    assert report["has_unsettled"] is True
    assert service.trial is not None
    with sqlite3.connect(config.database_path.with_name("live-preparation.sqlite3")) as connection:
        baseline = connection.execute(
            "SELECT account, balances_json FROM trial_account_baseline"
        ).fetchone()
        trial = connection.execute(
            "SELECT account,state,entries_enabled FROM signal_trial"
        ).fetchone()
        intents = connection.execute("SELECT COUNT(*) FROM trial_intents").fetchone()[0]
    assert baseline is not None and baseline[0] == credentials.fingerprint
    assert trial == (credentials.fingerprint, "WAITING_SIGNAL", 1)
    assert intents == 0  # arming never sends an order or invents a signal


def test_internal_arm_requires_current_successful_check(tmp_path) -> None:
    _, _, service = client_for(tmp_path, MemoryVault())
    with pytest.raises(Exception, match="Kontoprüfung"):
        service.arm_trial(notional=Decimal("50"))


def test_failed_arm_rolls_back_only_unused_baseline(tmp_path, monkeypatch) -> None:
    _, config, service, _ = ready_service(tmp_path)
    assert service.trial is not None

    def fail(*args, **kwargs):
        raise RuntimeError("synthetic arm failure")

    monkeypatch.setattr(service.trial, "arm", fail)
    with pytest.raises(RuntimeError, match="synthetic"):
        service.arm_trial(notional=Decimal("50"))
    with sqlite3.connect(config.database_path.with_name("live-preparation.sqlite3")) as connection:
        assert connection.execute("SELECT COUNT(*) FROM trial_account_baseline").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM signal_trial").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM trial_intents").fetchone()[0] == 0


def test_public_route_remains_closed_until_external_acceptance(tmp_path) -> None:
    client, _, service, _ = ready_service(tmp_path)
    body = {"confirmation": "TEST 50 USDC", "quote_asset": "USDC", "notional_quote": "50.00"}
    response = client.post("/api/live/trial/start", headers=HEADERS, json=body)
    assert response.status_code == 409
    assert service.trial is not None
    assert service.trial.report()["state"] == "NOT_STARTED"
    assert response.json()["trial_readiness"]["technical_release_ready"] is True
    assert response.json()["trial_readiness"]["production_submission_accepted"] is False


def test_wrong_amount_never_creates_baseline(tmp_path) -> None:
    _, config, service, _ = ready_service(tmp_path)
    with pytest.raises(Exception, match="genau 50"):
        service.arm_trial(notional=Decimal("49"))
    with sqlite3.connect(config.database_path.with_name("live-preparation.sqlite3")) as connection:
        assert connection.execute("SELECT COUNT(*) FROM trial_account_baseline").fetchone()[0] == 0
