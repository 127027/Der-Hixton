from __future__ import annotations

import json
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from hixton.cli import main
from hixton.config import load_project_config
from hixton.constants import SYMBOLS


def test_windows_runtime_timezone_is_available() -> None:
    assert ZoneInfo("Europe/Berlin").key == "Europe/Berlin"


def _payload() -> dict[str, object]:
    return {
        "schema_version": 1,
        "strategy": {
            "version": "HIXTON-SPEC-1.0",
            "timeframe": "1h",
            "source": "close",
            "vidya_length": 10,
            "momentum_length": 20,
            "smoothing_length": 15,
            "atr_length": 200,
            "band_multiplier": 2.0,
            "warmup_bars": 400,
            "long_only": True,
            "compounding": False,
        },
        "markets": list(SYMBOLS),
        "backtest": {
            "starting_usdt_per_symbol": "250.00",
            "target_notional_usdt": "250.00",
            "primary_window_years": 3,
            "run_baseline_and_stress": True,
        },
        "paper": {
            "starting_cash_usdt": "240.00",
            "slot_count": 3,
            "target_notional_usdt": "80.00",
            "poll_seconds": 30,
            "daily_audit_utc": "00:05",
        },
        "ui": {
            "bind": "127.0.0.1",
            "port": 8765,
            "timezone": "Europe/Berlin",
            "default_range": "1m",
        },
        "runtime": {
            "database_path": "data/hixton.sqlite3",
            "run_output_root": "backtests/v1/runs",
            "binance_base_url": "https://api.binance.com",
        },
    }


def _write(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_valid_v1_config_resolves_runtime_paths(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    _write(path, _payload())
    config = load_project_config(path, project_root=tmp_path)
    assert config.database_path == tmp_path / "data" / "hixton.sqlite3"
    assert config.ui_port == 8765
    assert config.paper_poll_seconds == 30


def test_unknown_or_changed_paper_baseline_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    payload = _payload()
    payload["unexpected"] = True
    _write(path, payload)
    with pytest.raises(ValueError, match="unknown root"):
        load_project_config(path, project_root=tmp_path)

    payload = _payload()
    paper = payload["paper"]
    assert isinstance(paper, dict)
    paper["slot_count"] = 4
    _write(path, payload)
    with pytest.raises(ValueError, match="3x80"):
        load_project_config(path, project_root=tmp_path)


def test_live_command_remains_technically_locked(capsys: pytest.CaptureFixture[str]) -> None:
    result = main(["live"])
    assert result == 2
    assert "sicher gesperrt" in capsys.readouterr().err
