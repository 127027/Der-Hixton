"""FastAPI surface for the localhost-only Hixton dashboard."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from hixton import __version__
from hixton.config import ProjectConfig
from hixton.constants import HIXTON_SPEC_VERSION, SYMBOLS
from hixton.paper.engine import load_paper_portfolio
from hixton.paper.models import PaperSettings
from hixton.paper.storage import PaperStore
from hixton.runtime.state import RuntimeSnapshot
from hixton.runtime.supervisor import RuntimeSupervisor
from hixton.ui.chart import RANGE_LABELS, build_chart_payload

STATIC_ROOT = Path(__file__).with_name("static")


def _iso(value: datetime | None) -> str | None:
    return value.astimezone(UTC).isoformat() if value is not None else None


def _runtime_payload(snapshot: RuntimeSnapshot) -> dict[str, object]:
    return {
        "health": snapshot.health,
        "mode": snapshot.mode,
        "live_state": "LIVE_DISABLED",
        "message": snapshot.message,
        "started_at_utc": _iso(snapshot.started_at_utc),
        "last_sync_utc": _iso(snapshot.last_sync_utc),
        "last_stream_update_utc": _iso(snapshot.last_stream_update_utc),
        "stream_connected": snapshot.stream_connected,
        "feed_mode": snapshot.feed_mode,
        "next_daily_audit_utc": _iso(snapshot.next_daily_audit_utc),
        "last_daily_audit_utc": _iso(snapshot.last_daily_audit_utc),
        "last_error": snapshot.last_error,
        "sync_in_progress": snapshot.sync_in_progress,
        "backtest_status": snapshot.backtest_status,
    }


def _latest_prices(supervisor: RuntimeSupervisor) -> dict[str, Decimal]:
    return {
        symbol: Decimal(str(points[-1].candle.close))
        for symbol, points in supervisor.state.points().items()
        if points
    }


def _paper_payload(
    supervisor: RuntimeSupervisor,
    config: ProjectConfig,
) -> dict[str, object] | None:
    try:
        portfolio = load_paper_portfolio(
            str(config.database_path),
            _latest_prices(supervisor),
        )
    except (OSError, RuntimeError):
        return None
    return {
        "cash_usdt": str(portfolio.account.cash_usdt),
        "starting_cash_usdt": str(portfolio.account.starting_cash_usdt),
        "equity_usdt": str(portfolio.equity_usdt),
        "unrealized_pnl_usdt": str(portfolio.unrealized_pnl_usdt),
        "high_water_equity_usdt": str(portfolio.account.high_water_equity_usdt),
        "drawdown_pct": str(portfolio.drawdown_pct),
        "daily_loss_paused": portfolio.daily_loss_paused,
        "halted": portfolio.account.halted,
        "halt_reason": portfolio.account.halt_reason,
        "settings": {
            "slot_count": portfolio.settings.slot_count,
            "target_notional_usdt": str(portfolio.settings.target_notional_usdt),
            "emergency_stop": portfolio.settings.emergency_stop,
        },
        "positions": [
            {
                "symbol": position.symbol,
                "quantity": str(position.quantity),
                "average_price": str(position.average_price),
                "cost_basis_usdt": str(position.cost_basis_usdt),
                "entry_time_utc": _iso(position.entry_time_utc),
                "entry_signal_id": position.entry_signal_id,
                "market_value_usdt": str(
                    position.quantity
                    * _latest_prices(supervisor).get(position.symbol, position.average_price)
                ),
            }
            for position in portfolio.positions
        ],
    }


def _market_payloads(
    supervisor: RuntimeSupervisor,
    config: ProjectConfig,
) -> list[dict[str, object]]:
    points_by_symbol = supervisor.state.points()
    quality = supervisor.state.quality()
    paper = _paper_payload(supervisor, config)
    raw_positions = paper.get("positions", []) if paper is not None else []
    position_items = raw_positions if isinstance(raw_positions, list) else []
    positions = {
        str(position["symbol"]): position
        for position in position_items
        if isinstance(position, dict) and "symbol" in position
    }
    payloads: list[dict[str, object]] = []
    for symbol in SYMBOLS:
        points = points_by_symbol.get(symbol, ())
        point = points[-1] if points else None
        last_signal = None
        if points:
            for candidate in reversed(points):
                if candidate.flip_up or candidate.flip_down:
                    last_signal = {
                        "action": "ENTER_LONG" if candidate.flip_up else "EXIT_LONG",
                        "time_utc": _iso(candidate.candle.close_time_utc),
                    }
                    break
        report = quality.get(symbol)
        payloads.append(
            {
                "symbol": symbol,
                "display_symbol": symbol.removesuffix("USDT") + "/USDT",
                "available": point is not None,
                "price": point.candle.close if point else None,
                "price_time_utc": _iso(point.candle.close_time_utc) if point else None,
                "trend": point.trend.value if point else "UNINITIALIZED",
                "last_signal": last_signal,
                "position": positions.get(symbol),
                "position_state": "LONG" if symbol in positions else "FLAT",
                "data": {
                    "candle_count": report.candle_count if report else 0,
                    "first_open_utc": _iso(report.first_open_time_utc) if report else None,
                    "last_open_utc": _iso(report.last_open_time_utc) if report else None,
                    "gap_count": report.gap_count if report else None,
                    "valid": report.valid if report else False,
                },
            }
        )
    return payloads


def _list_backtests(output_root: Path) -> list[dict[str, object]]:
    if not output_root.exists():
        return []
    entries: list[dict[str, object]] = []
    directories = sorted(
        (item for item in output_root.iterdir() if item.is_dir()),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for directory in directories[:25]:
        manifest_path = directory / "manifest.json"
        metrics_path = directory / "metrics.json"
        if not manifest_path.exists() or not metrics_path.exists():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        entries.append({"manifest": manifest, "metrics": metrics})
    return entries


def _origin_is_local(request: Request) -> bool:
    origin = request.headers.get("origin")
    action_header = request.headers.get("x-hixton-action")
    local_origin = origin is None or origin.startswith(
        ("http://127.0.0.1:", "http://localhost:")
    )
    return local_origin and action_header == "local-ui-v1"


def create_app(config: ProjectConfig, supervisor: RuntimeSupervisor) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        supervisor.start()
        yield
        await supervisor.stop()

    app = FastAPI(
        title="Der Hixton",
        version=__version__,
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])

    @app.middleware("http")
    async def security_headers(request: Request, call_next: Any) -> Any:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; font-src 'self'; frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        return response
    app.mount("/assets", StaticFiles(directory=STATIC_ROOT / "assets"), name="assets")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_ROOT / "index.html")

    @app.get("/api/status")
    def status() -> dict[str, object]:
        return {
            "application": "Der Hixton Trading Bot",
            "application_version": __version__,
            "strategy_version": HIXTON_SPEC_VERSION,
            "runtime": _runtime_payload(supervisor.state.snapshot()),
            "paper": _paper_payload(supervisor, config),
            "server_time_utc": _iso(datetime.now(UTC)),
            "ui_timezone": config.ui_timezone,
        }

    @app.get("/api/markets")
    def markets() -> dict[str, object]:
        return {"markets": _market_payloads(supervisor, config)}

    @app.get("/api/chart")
    def chart(
        symbol: str = Query(...),
        range_key: str = Query("1m", alias="range"),
        timezone: str = Query("Europe/Berlin"),
    ) -> dict[str, object]:
        normalized = symbol.replace("/", "").upper()
        if normalized not in SYMBOLS:
            raise HTTPException(status_code=400, detail="Unbekanntes DMS-Symbol")
        if range_key not in RANGE_LABELS:
            raise HTTPException(status_code=400, detail="Unbekannter Chartzeitraum")
        points = supervisor.state.points().get(normalized, ())
        try:
            with PaperStore(config.database_path) as store:
                events = store.load_events(symbol=normalized, limit=5_000)
        except (OSError, sqlite3.Error):
            events = ()
        try:
            return build_chart_payload(
                symbol=normalized,
                points=points,
                range_key=range_key,
                timezone_name=timezone,
                now=datetime.now(UTC),
                paper_events=events,
            )
        except (ValueError, ZoneInfoNotFoundError) as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.get("/api/paper/events")
    def paper_events(symbol: str | None = None, limit: int = 250) -> dict[str, object]:
        with PaperStore(config.database_path) as store:
            store.initialize()
            events = store.load_events(symbol=symbol, limit=limit)
        return {
            "events": [
                {
                    **asdict(event),
                    "status": event.status.value,
                    "occurred_at_utc": _iso(event.occurred_at_utc),
                }
                for event in events
            ]
        }

    @app.post("/api/paper/settings")
    async def paper_settings(request: Request) -> dict[str, object]:
        if not _origin_is_local(request):
            raise HTTPException(status_code=403, detail="Nur lokale UI-Aufrufe sind erlaubt")
        payload: Any = await request.json()
        if not isinstance(payload, dict) or payload.get("confirmation") != "ANWENDEN":
            raise HTTPException(status_code=400, detail="Bestaetigung ANWENDEN fehlt")
        try:
            settings = PaperSettings(
                slot_count=int(payload["slot_count"]),
                target_notional_usdt=Decimal(str(payload["target_notional_usdt"])),
                emergency_stop=bool(payload.get("emergency_stop", False)),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        with PaperStore(config.database_path) as store:
            store.initialize()
            store.save_settings(settings)
        return {"saved": True, "settings": asdict(settings)}

    @app.post("/api/data/sync")
    async def data_sync(request: Request) -> dict[str, object]:
        if not _origin_is_local(request):
            raise HTTPException(status_code=403, detail="Nur lokale UI-Aufrufe sind erlaubt")
        await supervisor.request_sync()
        return {"started": True, "status": _runtime_payload(supervisor.state.snapshot())}

    @app.get("/api/data-quality")
    def data_quality() -> dict[str, object]:
        reports = supervisor.state.quality()
        return {
            "reports": [
                {
                    "symbol": symbol,
                    "valid": report.valid,
                    "candle_count": report.candle_count,
                    "expected_count": report.expected_count,
                    "first_open_utc": _iso(report.first_open_time_utc),
                    "last_open_utc": _iso(report.last_open_time_utc),
                    "gap_count": report.gap_count,
                    "issues": [asdict(issue) for issue in report.issues[:20]],
                }
                for symbol, report in reports.items()
            ]
        }

    @app.get("/api/backtests")
    def backtests() -> dict[str, object]:
        return {
            "runs": _list_backtests(config.run_output_root),
            "status": supervisor.state.snapshot().backtest_status,
        }

    @app.get("/api/logs")
    def logs(limit: int = 250) -> dict[str, object]:
        try:
            entries = supervisor.state.logs(limit=limit)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        return {
            "logs": [
                {
                    **asdict(entry),
                    "time_utc": _iso(entry.time_utc),
                }
                for entry in entries
            ]
        }

    @app.post("/api/backtests/run")
    async def run_backtest(request: Request) -> dict[str, object]:
        if not _origin_is_local(request):
            raise HTTPException(status_code=403, detail="Nur lokale UI-Aufrufe sind erlaubt")
        payload: Any = await request.json()
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Ungueltige Backtest-Anfrage")
        try:
            started = supervisor.start_backtest(
                mode=str(payload.get("mode", "")),
                symbol=str(payload.get("symbol")) if payload.get("symbol") else None,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        if not started:
            raise HTTPException(status_code=409, detail="Ein Backtest laeuft bereits")
        return {"started": True, "status": "RUNNING"}

    return app
