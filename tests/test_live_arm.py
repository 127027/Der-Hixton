from __future__ import annotations

import sqlite3
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from hixton.constants import SYMBOLS
from hixton.live.credentials import BinanceCredentials, CredentialService
from hixton.live.reconciliation import AccountSnapshot
from hixton.paper.storage import PaperStore
from hixton.runtime.supervisor import RuntimeSupervisor
from hixton.ui.api import create_app
from tests.test_live_preparation import (
    HEADERS,
    MemoryVault,
    client_for,
    config_for,
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
    assert intents == 0


def test_armed_entitlement_does_not_expire_with_old_ui_preflight(tmp_path) -> None:
    _, _, service, _ = ready_service(tmp_path)
    service.arm_trial(notional=Decimal("50"))
    service._check_time = 0
    assert service.technical_release_ready() is False
    assert service.execution_release_ready() is True


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


def test_production_public_route_stays_fail_closed(tmp_path) -> None:
    client, _, service, _ = ready_service(tmp_path)
    body = {"confirmation": "TEST 50 USDC", "quote_asset": "USDC", "notional_quote": "50.00"}
    response = client.post("/api/live/trial/start", headers=HEADERS, json=body)
    assert response.status_code == 409
    assert service.trial is not None
    assert service.trial.report()["state"] == "NOT_STARTED"
    assert response.json()["trial_readiness"]["technical_release_ready"] is True
    assert response.json()["trial_readiness"]["production_submission_accepted"] is False


def test_testnet_public_route_can_only_arm_after_fresh_testnet_check(tmp_path) -> None:
    config = replace(config_for(tmp_path), trial_order_base_url="https://testnet.binance.vision")
    supervisor = RuntimeSupervisor(config)
    with PaperStore(config.database_path) as store:
        store.initialize(
            strategy_key="v6",
            strategy_version=supervisor.strategy.version,
            starting_cash_usdc=Decimal("250"),
        )
        checkpoints = dict.fromkeys(SYMBOLS, datetime.now(UTC))
        store.save_checkpoints(checkpoints)
        store.ensure_soak_started(checkpoints)
    vault = MemoryVault()
    app = create_app(config, supervisor, live_vault=vault)
    client = TestClient(app, base_url="http://127.0.0.1:8765")
    service = app.state.live_preparation
    unlock(client)
    save_key(client)
    credentials = service.credentials.load()
    assert credentials is not None
    assert service.credentials.record_name == "binance-hmac-testnet"

    service._inspect_testnet = lambda _: {
        "account_checks_passed": True,
        "blockers": [],
        "free_usdc": "100",
        "free_bnb": "0",
        "environment": "TESTNET",
        "production_api_permissions_verified": False,
    }
    assert client.post("/api/live/check", headers=HEADERS, json={}).status_code == 200
    service.snapshot_reader = lambda: AccountSnapshot(
        credentials.fingerprint,
        datetime.now(UTC),
        {"USDC": (Decimal("100"), Decimal("0"))},
        (),
    )
    body = {"confirmation": "TEST 50 USDC", "quote_asset": "USDC", "notional_quote": "50.00"}
    response = client.post("/api/live/trial/start", headers=HEADERS, json=body)
    assert response.status_code == 200
    assert response.json()["trial_environment"] == "TESTNET"
    assert response.json()["trial"]["state"] == "WAITING_SIGNAL"


def test_production_and_testnet_credentials_are_separate() -> None:
    vault = MemoryVault()
    prod = CredentialService(vault)
    testnet = CredentialService(vault, record_name="binance-hmac-testnet")
    prod_key = BinanceCredentials("A" * 32, "B" * 32)
    test_key = BinanceCredentials("C" * 32, "D" * 32)
    prod.save(prod_key)
    testnet.save(test_key)
    assert prod.load() is not None and prod.load().api_key == "A" * 32
    assert testnet.load() is not None and testnet.load().api_key == "C" * 32
    testnet.delete()
    assert testnet.load() is None
    assert prod.load() is not None


def test_wrong_amount_never_creates_baseline(tmp_path) -> None:
    _, config, service, _ = ready_service(tmp_path)
    with pytest.raises(Exception, match="genau 50"):
        service.arm_trial(notional=Decimal("49"))
    with sqlite3.connect(config.database_path.with_name("live-preparation.sqlite3")) as connection:
        assert connection.execute("SELECT COUNT(*) FROM trial_account_baseline").fetchone()[0] == 0
