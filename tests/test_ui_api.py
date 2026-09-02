from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient

from hixton.config import ProjectConfig
from hixton.constants import SYMBOLS
from hixton.paper.storage import PaperStore
from hixton.runtime.supervisor import RuntimeSupervisor
from hixton.ui.api import create_app


def _config(tmp_path: Path) -> ProjectConfig:
    return ProjectConfig(
        strategy_key="v2",
        database_path=tmp_path / "hixton.sqlite3",
        run_output_root=tmp_path / "backtests" / "v2" / "runs",
        binance_base_url="https://api.binance.com",
        starting_usdt_per_symbol=Decimal("250.00"),
        target_notional_usdt=Decimal("250.00"),
        run_baseline_and_stress=True,
        paper_poll_seconds=30,
        paper_starting_cash_usdt=Decimal("240.00"),
        paper_slot_count=3,
        paper_target_notional_usdt=Decimal("80.00"),
        daily_audit_utc="00:05",
        ui_bind="127.0.0.1",
        ui_port=8765,
        ui_timezone="Europe/Berlin",
        ui_default_range="1m",
        sha256="test-config",
    )


def test_local_ui_status_and_ten_market_placeholders(tmp_path: Path) -> None:
    config = _config(tmp_path)
    client = TestClient(
        create_app(config, RuntimeSupervisor(config)),
        base_url="http://127.0.0.1:8765",
    )
    status = client.get("/api/status")
    assert status.status_code == 200
    assert status.json()["runtime"]["live_state"] == "LIVE_DISABLED"
    assert status.headers["x-frame-options"] == "DENY"
    markets = client.get("/api/markets")
    assert markets.status_code == 200
    assert [item["symbol"] for item in markets.json()["markets"]] == list(SYMBOLS)
    logs = client.get("/api/logs")
    assert logs.status_code == 200
    assert logs.json()["logs"][0]["event_code"] == "PROCESS_START"


def test_setting_write_requires_local_action_header_and_confirmation(tmp_path: Path) -> None:
    config = _config(tmp_path)
    client = TestClient(
        create_app(config, RuntimeSupervisor(config)),
        base_url="http://127.0.0.1:8765",
    )
    payload = {
        "slot_count": 4,
        "target_notional_usdt": "60.00",
        "emergency_stop": True,
        "confirmation": "ANWENDEN",
    }
    denied = client.post("/api/paper/settings", json=payload)
    assert denied.status_code == 403
    saved = client.post(
        "/api/paper/settings",
        json=payload,
        headers={"X-Hixton-Action": "local-ui-v1", "Origin": "http://127.0.0.1:8765"},
    )
    assert saved.status_code == 200
    with PaperStore(config.database_path) as store:
        settings = store.load_settings()
    assert settings.slot_count == 4
    assert settings.target_notional_usdt == Decimal("60.00")
    assert settings.emergency_stop is True


def test_status_exposes_restart_persistent_paper_soak_gate(tmp_path: Path) -> None:
    config = _config(tmp_path)
    started = datetime.now(UTC)
    checkpoints = dict.fromkeys(SYMBOLS, started)
    with PaperStore(config.database_path) as store:
        store.initialize(
            at=started,
            strategy_key="v2",
            strategy_version="HIXTON-V2-RESEARCH-CANDIDATE-1",
        )
        store.save_checkpoints(checkpoints)
        store.ensure_soak_started(checkpoints, at=started)
    client = TestClient(
        create_app(config, RuntimeSupervisor(config)),
        base_url="http://127.0.0.1:8765",
    )
    paper = client.get("/api/status").json()["paper"]
    assert paper["soak"]["status"] == "RUNNING"
    assert paper["soak"]["minimum_processed_closed_bars"] == 0
    assert paper["soak"]["completed_trades"] == 0
    assert paper["soak"]["ready"] is False


def test_backtest_api_keeps_v1_and_v2_run_views_separate(tmp_path: Path) -> None:
    config = _config(tmp_path)
    client = TestClient(
        create_app(config, RuntimeSupervisor(config)),
        base_url="http://127.0.0.1:8765",
    )

    v1 = client.get("/api/backtests?strategy=v1")
    v2 = client.get("/api/backtests?strategy=v2")
    invalid = client.get("/api/backtests?strategy=unknown")

    assert v1.status_code == 200
    assert v1.json()["strategy"]["version"] == "HIXTON-SPEC-1.0"
    assert v1.json()["strategy"]["paper_approved"] is False
    assert v2.status_code == 200
    assert v2.json()["strategy"]["version"] == "HIXTON-V2-RESEARCH-CANDIDATE-1"
    assert v2.json()["strategy"]["paper_approved"] is True
    assert invalid.status_code == 400
