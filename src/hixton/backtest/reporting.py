"""Immutable JSON/CSV/HTML report bundle writer for single and batch runs."""

from __future__ import annotations

import csv
import dataclasses
import html
import json
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import TypeAlias
from uuid import uuid4

from hixton.backtest.models import BacktestResult, BatchResult
from hixton.constants import HIXTON_SPEC_VERSION, TIMEFRAME

RunResult: TypeAlias = BacktestResult | BatchResult


def _primitive(value: object) -> object:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _primitive(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _primitive(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_primitive(item) for item in value]
    return value


def _single_results(result: RunResult) -> tuple[BacktestResult, ...]:
    return result.results if isinstance(result, BatchResult) else (result,)


def write_report_bundle(
    *,
    scenarios: dict[str, RunResult],
    output_root: Path,
    config_sha256: str,
    code_commit: str,
    report_start_utc: datetime,
    report_end_utc: datetime,
) -> Path:
    """Create one new run directory; existing runs are never overwritten."""

    run_id = str(uuid4())
    run_directory = output_root / run_id
    run_directory.mkdir(parents=True, exist_ok=False)
    created_at = datetime.now(UTC)

    data_hashes: dict[str, str] = {}
    for result in scenarios.values():
        for single in _single_results(result):
            data_hashes[single.symbol] = single.data_snapshot_sha256

    metrics_payload = {
        scenario: (
            {
                "batch": {
                    field.name: _primitive(getattr(result, field.name))
                    for field in dataclasses.fields(result)
                    if field.name != "results"
                },
                "per_symbol": {
                    single.symbol: _primitive(single.metrics)
                    for single in _single_results(result)
                },
            }
            if isinstance(result, BatchResult)
            else {"per_symbol": {result.symbol: _primitive(result.metrics)}}
        )
        for scenario, result in scenarios.items()
    }
    (run_directory / "metrics.json").write_text(
        json.dumps(metrics_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_trades(run_directory / "trades.csv", scenarios)
    _write_equity(run_directory / "equity.csv", scenarios)
    _write_html(run_directory / "report.html", run_id, metrics_payload)

    manifest = {
        "schema_version": 1,
        "backtest_version": "v1",
        "run_id": run_id,
        "created_at_utc": created_at.isoformat(),
        "status": "VALID",
        "strategy": {
            "version": HIXTON_SPEC_VERSION,
            "normative_spec": "DMS/03_STRATEGIE_HIXTON.md",
            "code_commit": code_commit,
            "config_sha256": config_sha256,
        },
        "data": {
            "provider": "binance_spot",
            "timeframe": TIMEFRAME,
            "report_start_utc": report_start_utc.astimezone(UTC).isoformat(),
            "report_end_utc": report_end_utc.astimezone(UTC).isoformat(),
            "snapshot_sha256_by_symbol": data_hashes,
        },
        "scenarios": sorted(scenarios),
        "artifacts": ["metrics.json", "trades.csv", "equity.csv", "report.html"],
        "warning": "Historical results are not a profit guarantee.",
    }
    (run_directory / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return run_directory


def _write_trades(path: Path, scenarios: dict[str, RunResult]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            (
                "scenario",
                "symbol",
                "entry_time_utc",
                "exit_time_utc",
                "entry_signal_id",
                "exit_signal_id",
                "entry_quote_spend",
                "exit_quote_receive",
                "realized_pnl",
                "realized_return_pct",
                "holding_hours",
                "residual_dust_quantity",
            )
        )
        for scenario, result in scenarios.items():
            for single in _single_results(result):
                for trade in single.trades:
                    writer.writerow(
                        (
                            scenario,
                            trade.symbol,
                            trade.entry_time_utc.isoformat(),
                            trade.exit_time_utc.isoformat(),
                            trade.entry_signal_id,
                            trade.exit_signal_id,
                            trade.entry_quote_spend,
                            trade.exit_quote_receive,
                            trade.realized_pnl,
                            trade.realized_return_pct,
                            trade.holding_hours,
                            trade.residual_dust_quantity,
                        )
                    )


def _write_equity(path: Path, scenarios: dict[str, RunResult]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("scenario", "symbol", "time_utc", "cash", "position_value", "equity"))
        for scenario, result in scenarios.items():
            for single in _single_results(result):
                for point in single.equity_curve:
                    writer.writerow(
                        (
                            scenario,
                            single.symbol,
                            point.time_utc.isoformat(),
                            point.cash,
                            point.position_value,
                            point.equity,
                        )
                    )


def _write_html(path: Path, run_id: str, metrics_payload: object) -> None:
    payload = html.escape(json.dumps(metrics_payload, ensure_ascii=False, indent=2))
    document = f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hixton Backtest {html.escape(run_id)}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #172033; }}
    pre {{ white-space: pre-wrap; background: #f3f5f8; padding: 1rem; border-radius: .5rem; }}
    .warning {{ border-left: .3rem solid #b26a00; padding-left: 1rem; }}
  </style>
</head>
<body>
  <h1>Hixton Backtest V1</h1>
  <p>Run-ID: <code>{html.escape(run_id)}</code></p>
  <p class="warning">Historische Ergebnisse sind keine Gewinngarantie.</p>
  <h2>Kennzahlen</h2>
  <pre>{payload}</pre>
</body>
</html>
"""
    path.write_text(document, encoding="utf-8")
