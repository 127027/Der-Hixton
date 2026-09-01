"""Strict, secret-free JSON configuration for the implemented V1 foundation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from hixton.constants import HIXTON_SPEC_VERSION, SYMBOLS, TIMEFRAME
from hixton.domain.models import StrategyParameters


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    database_path: Path
    run_output_root: Path
    binance_base_url: str
    starting_usdt_per_symbol: Decimal
    target_notional_usdt: Decimal
    run_baseline_and_stress: bool
    paper_poll_seconds: int
    daily_audit_utc: str
    ui_bind: str
    ui_port: int
    ui_timezone: str
    ui_default_range: str
    sha256: str


def _required_mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _reject_unknown(mapping: dict[str, Any], allowed: set[str], name: str) -> None:
    unknown = set(mapping) - allowed
    if unknown:
        raise ValueError(f"unknown {name} fields: {', '.join(sorted(unknown))}")


def load_project_config(path: Path, *, project_root: Path) -> ProjectConfig:
    raw_text = path.read_text(encoding="utf-8")
    payload = json.loads(raw_text)
    root = _required_mapping(payload, "configuration")
    _reject_unknown(
        root,
        {"schema_version", "strategy", "markets", "backtest", "paper", "ui", "runtime"},
        "root",
    )
    if root.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")

    strategy = _required_mapping(root.get("strategy"), "strategy")
    expected_strategy: dict[str, object] = {
        "version": HIXTON_SPEC_VERSION,
        "timeframe": TIMEFRAME,
        "source": "close",
        "vidya_length": 10,
        "momentum_length": 20,
        "smoothing_length": 15,
        "atr_length": 200,
        "band_multiplier": 2.0,
        "warmup_bars": 400,
        "long_only": True,
        "compounding": False,
    }
    _reject_unknown(strategy, set(expected_strategy), "strategy")
    if strategy != expected_strategy:
        differences = sorted(
            key for key, expected in expected_strategy.items() if strategy.get(key) != expected
        )
        raise ValueError(f"configuration deviates from HIXTON-SPEC-1.0: {differences}")
    StrategyParameters()

    markets = root.get("markets")
    if not isinstance(markets, list) or tuple(markets) != SYMBOLS:
        raise ValueError("markets must contain the ten DMS symbols in fixed order")

    backtest = _required_mapping(root.get("backtest"), "backtest")
    _reject_unknown(
        backtest,
        {
            "starting_usdt_per_symbol",
            "target_notional_usdt",
            "primary_window_years",
            "run_baseline_and_stress",
        },
        "backtest",
    )
    if backtest.get("primary_window_years") != 3:
        raise ValueError("primary_window_years must be 3")
    starting = Decimal(str(backtest.get("starting_usdt_per_symbol")))
    target = Decimal(str(backtest.get("target_notional_usdt")))
    if starting != Decimal("250.00") or target != Decimal("250.00"):
        raise ValueError("isolated V1 backtests require fixed 250.00 USDT")

    paper = _required_mapping(root.get("paper"), "paper")
    expected_paper: dict[str, object] = {
        "starting_cash_usdt": "240.00",
        "slot_count": 3,
        "target_notional_usdt": "80.00",
        "poll_seconds": 30,
        "daily_audit_utc": "00:05",
    }
    _reject_unknown(paper, set(expected_paper), "paper")
    if paper != expected_paper:
        raise ValueError("paper baseline must remain 240 USDT with 3x80 USDT")

    ui = _required_mapping(root.get("ui"), "ui")
    expected_ui: dict[str, object] = {
        "bind": "127.0.0.1",
        "port": 8765,
        "timezone": "Europe/Berlin",
        "default_range": "1m",
    }
    _reject_unknown(ui, set(expected_ui), "ui")
    if ui != expected_ui:
        raise ValueError("UI baseline must use the documented local V1 settings")

    runtime = _required_mapping(root.get("runtime"), "runtime")
    _reject_unknown(runtime, {"database_path", "run_output_root", "binance_base_url"}, "runtime")
    database_path = project_root / str(runtime.get("database_path", "data/hixton.sqlite3"))
    run_output_root = project_root / str(runtime.get("run_output_root", "backtests/v1/runs"))
    digest = hashlib.sha256(
        json.dumps(root, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return ProjectConfig(
        database_path=database_path,
        run_output_root=run_output_root,
        binance_base_url=str(runtime.get("binance_base_url", "https://api.binance.com")),
        starting_usdt_per_symbol=starting,
        target_notional_usdt=target,
        run_baseline_and_stress=bool(backtest.get("run_baseline_and_stress", True)),
        paper_poll_seconds=int(paper["poll_seconds"]),
        daily_audit_utc=str(paper["daily_audit_utc"]),
        ui_bind=str(ui["bind"]),
        ui_port=int(ui["port"]),
        ui_timezone=str(ui["timezone"]),
        ui_default_range=str(ui["default_range"]),
        sha256=digest,
    )
