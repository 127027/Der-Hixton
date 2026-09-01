"""Startup recovery, Binance stream, REST fallback and the 00:05 UTC audit."""

from __future__ import annotations

import asyncio
import json
import subprocess
from contextlib import suppress
from datetime import UTC, datetime, timedelta

import websockets

from hixton.backtest.engine import run_isolated_batch, run_single_backtest
from hixton.backtest.models import BASELINE_COSTS, STRESS_COSTS, ExecutionRules
from hixton.backtest.reporting import RunResult, write_report_bundle
from hixton.config import ProjectConfig
from hixton.constants import SYMBOLS, TIMEFRAME_DELTA
from hixton.data.binance import BinancePublicClient, parse_websocket_kline
from hixton.data.quality import DataQualityReport
from hixton.data.storage import CandleStore
from hixton.data.sync import synchronize_symbol
from hixton.domain.models import Candle, IndicatorPoint
from hixton.paper.engine import initialize_paper_at_latest, process_new_closed_points
from hixton.runtime.analysis import rebuild_analysis
from hixton.runtime.state import RuntimeState


def _subtract_calendar_years(value: datetime, years: int) -> datetime:
    try:
        return value.replace(year=value.year - years)
    except ValueError:
        return value.replace(year=value.year - years, month=2, day=28)


def safe_closed_window(now: datetime | None = None) -> tuple[datetime, datetime, datetime]:
    current = (now or datetime.now(UTC)).astimezone(UTC)
    report_end = current.replace(minute=0, second=0, microsecond=0)
    if current - report_end < timedelta(minutes=2):
        report_end -= TIMEFRAME_DELTA
    report_start = _subtract_calendar_years(report_end, 3)
    return report_start - 400 * TIMEFRAME_DELTA, report_start, report_end


def next_daily_audit(now: datetime | None = None) -> datetime:
    current = (now or datetime.now(UTC)).astimezone(UTC)
    candidate = current.replace(hour=0, minute=5, second=0, microsecond=0)
    return candidate if candidate > current else candidate + timedelta(days=1)


class RuntimeSupervisor:
    """Own all long-running work; the API only reads snapshots or requests actions."""

    def __init__(self, config: ProjectConfig) -> None:
        self.config = config
        self.state = RuntimeState(next_daily_audit_utc=next_daily_audit())
        self._stop = asyncio.Event()
        self._closed_bar_event = asyncio.Event()
        self._sync_lock = asyncio.Lock()
        self._task: asyncio.Task[None] | None = None
        self._backtest_task_handle: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run(), name="hixton-runtime")

    async def stop(self) -> None:
        self.state.set_status(health="STOPPING", message="Geordnetes Herunterfahren")
        self._stop.set()
        if self._task is not None:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        if self._backtest_task_handle is not None:
            self._backtest_task_handle.cancel()
            with suppress(asyncio.CancelledError):
                await self._backtest_task_handle

    async def request_sync(self) -> None:
        await self._sync_and_analyze(initial=False)

    def start_backtest(self, *, mode: str, symbol: str | None = None) -> bool:
        if self.state.snapshot().backtest_status == "RUNNING":
            return False
        if mode not in {"all", "single"}:
            raise ValueError("backtest mode must be all or single")
        normalized = symbol.replace("/", "").upper() if symbol else None
        if mode == "single" and normalized not in SYMBOLS:
            raise ValueError("single backtest requires one DMS symbol")
        self.state.set_status(backtest_status="RUNNING")
        self._backtest_task_handle = asyncio.create_task(
            self._backtest_task(mode=mode, symbol=normalized),
            name="hixton-backtest",
        )
        return True

    async def _backtest_task(self, *, mode: str, symbol: str | None) -> None:
        try:
            await asyncio.to_thread(self._synchronous_backtest, mode, symbol)
            self.state.set_status(backtest_status="COMPLETE")
            self.state.log(
                level="INFO",
                component="backtest",
                event_code="BACKTEST_COMPLETE",
                message=f"Backtest {mode} {symbol or 'ALL'} erfolgreich abgeschlossen",
            )
        except Exception as error:
            self.state.set_status(backtest_status="FAILED", last_error=str(error))

    async def _run(self) -> None:
        initialized = False
        while not self._stop.is_set() and not initialized:
            try:
                await self._sync_and_analyze(initial=True)
                initialized = True
            except Exception as error:
                self.state.set_status(
                    health="DEGRADED",
                    message="Startup-Synchronisation fehlgeschlagen; neuer Versuch folgt",
                    last_error=str(error),
                    feed_mode="REST_RETRY",
                )
                await asyncio.sleep(30)
        if not initialized:
            return

        websocket_task = asyncio.create_task(self._stream_loop(), name="hixton-binance-stream")
        try:
            await self._watchdog_loop()
        finally:
            websocket_task.cancel()
            with suppress(asyncio.CancelledError):
                await websocket_task

    async def _sync_and_analyze(self, *, initial: bool, daily: bool = False) -> None:
        if self._sync_lock.locked():
            return
        async with self._sync_lock:
            self.state.set_status(
                sync_in_progress=True,
                message="Marktdaten und Binance-Filter werden synchronisiert",
            )
            try:
                points, quality, rules = await asyncio.to_thread(self._synchronous_sync)
                self.state.replace_analysis(points, quality)
                if initial:
                    await asyncio.to_thread(
                        initialize_paper_at_latest,
                        str(self.config.database_path),
                        points,
                    )
                else:
                    events = await asyncio.to_thread(
                        process_new_closed_points,
                        str(self.config.database_path),
                        points,
                        rules,
                    )
                    if events:
                        self.state.log(
                            level="INFO",
                            component="paper",
                            event_code="PAPER_BAR_PROCESSED",
                            message=f"{len(events)} Paper-Ereignisse persistiert",
                        )
                now = datetime.now(UTC)
                update: dict[str, object] = {
                    "health": "HEALTHY",
                    "message": "Paper-Betrieb aktiv; alle zehn Maerkte sind geprueft",
                    "last_sync_utc": now,
                    "last_error": None,
                    "sync_in_progress": False,
                    "next_daily_audit_utc": next_daily_audit(now),
                }
                if daily:
                    update["last_daily_audit_utc"] = now
                self.state.set_status(**update)
            except Exception:
                self.state.set_status(sync_in_progress=False)
                raise

    def _synchronous_sync(
        self,
    ) -> tuple[
        dict[str, tuple[IndicatorPoint, ...]],
        dict[str, DataQualityReport],
        dict[str, ExecutionRules],
    ]:
        warmup_start, _, report_end = safe_closed_window()
        client = BinancePublicClient(base_url=self.config.binance_base_url)
        clock_delta = abs((client.server_time() - datetime.now(UTC)).total_seconds())
        if clock_delta > 5:
            raise RuntimeError(f"Systemuhr weicht {clock_delta:.1f} Sekunden von Binance ab")
        with CandleStore(self.config.database_path) as store:
            if not store.integrity_check():
                raise RuntimeError("SQLite integrity check failed")
            for symbol in SYMBOLS:
                synchronize_symbol(
                    client=client,
                    store=store,
                    symbol=symbol,
                    start=warmup_start,
                    end_exclusive=report_end,
                )
        points, quality = rebuild_analysis(
            self.config.database_path,
            start=warmup_start,
            end_exclusive=report_end,
        )
        rules: dict[str, ExecutionRules] = {}
        with CandleStore(self.config.database_path) as store:
            for symbol in SYMBOLS:
                stored = store.load_symbol_rules(symbol)
                if stored is None:
                    raise RuntimeError(f"Binance filters missing for {symbol}")
                rules[symbol] = ExecutionRules(
                    tick_size=stored.tick_size,
                    step_size=stored.step_size,
                    min_qty=stored.min_qty,
                    min_notional=stored.min_notional,
                )
        return points, quality, rules

    def _synchronous_backtest(self, mode: str, symbol: str | None) -> None:
        _, report_start, report_end = safe_closed_window()
        points = self.state.points()
        if set(points) != set(SYMBOLS):
            raise RuntimeError("backtest requires synchronized data for all ten symbols")
        candles = {
            item_symbol: [point.candle for point in symbol_points]
            for item_symbol, symbol_points in points.items()
        }
        rules: dict[str, ExecutionRules] = {}
        with CandleStore(self.config.database_path) as store:
            for item_symbol in SYMBOLS:
                stored = store.load_symbol_rules(item_symbol)
                if stored is None:
                    raise RuntimeError(f"Binance filters missing for {item_symbol}")
                rules[item_symbol] = ExecutionRules(
                    tick_size=stored.tick_size,
                    step_size=stored.step_size,
                    min_qty=stored.min_qty,
                    min_notional=stored.min_notional,
                )
        scenarios: dict[str, RunResult] = {}
        for costs in (BASELINE_COSTS, STRESS_COSTS):
            if mode == "all":
                scenarios[costs.name] = run_isolated_batch(
                    candles_by_symbol=candles,
                    report_start_utc=report_start,
                    report_end_utc=report_end,
                    costs=costs,
                    execution_rules=rules,
                )
            else:
                if symbol is None:
                    raise RuntimeError("single backtest symbol disappeared")
                scenarios[costs.name] = run_single_backtest(
                    symbol=symbol,
                    candles=candles[symbol],
                    report_start_utc=report_start,
                    report_end_utc=report_end,
                    starting_cash=self.config.starting_usdt_per_symbol,
                    target_notional=self.config.target_notional_usdt,
                    costs=costs,
                    execution_rules=rules[symbol],
                )
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.config.run_output_root.parents[2],
            capture_output=True,
            check=False,
            text=True,
        )
        code_commit = completed.stdout.strip() if completed.returncode == 0 else "UNKNOWN"
        write_report_bundle(
            scenarios=scenarios,
            output_root=self.config.run_output_root,
            config_sha256=self.config.sha256,
            code_commit=code_commit,
            report_start_utc=report_start,
            report_end_utc=report_end,
        )

    async def _stream_loop(self) -> None:
        streams = "/".join(f"{symbol.lower()}@kline_1h" for symbol in SYMBOLS)
        url = f"wss://stream.binance.com:9443/stream?streams={streams}"
        delay = 1
        while not self._stop.is_set():
            try:
                async with websockets.connect(
                    url,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=5,
                    max_size=1_000_000,
                ) as websocket:
                    recovery_required = delay > 1
                    self.state.set_status(
                        stream_connected=True,
                        feed_mode="WEBSOCKET",
                        message="Paper-Betrieb aktiv; Binance-Livestream verbunden",
                        last_stream_update_utc=datetime.now(UTC),
                    )
                    delay = 1
                    if recovery_required:
                        self._closed_bar_event.set()
                    async for raw_message in websocket:
                        payload = json.loads(raw_message)
                        candle = parse_websocket_kline(payload)
                        self.state.set_status(last_stream_update_utc=datetime.now(UTC))
                        if candle.closed:
                            self._closed_bar_event.set()
                        else:
                            await asyncio.to_thread(self._store_stream_candle, candle)
                        if self._stop.is_set():
                            break
            except asyncio.CancelledError:
                raise
            except Exception as error:
                self.state.set_status(
                    stream_connected=False,
                    feed_mode="REST_FALLBACK",
                    health="DEGRADED",
                    message="Livestream getrennt; REST-Recovery aktiv",
                    last_error=str(error),
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, 60)

    def _store_stream_candle(self, candle: Candle) -> None:
        with CandleStore(self.config.database_path) as store:
            store.put_candles((candle,), revision_reason="stream_update")

    async def _watchdog_loop(self) -> None:
        rest_recovery_hour: datetime | None = None
        while not self._stop.is_set():
            now = datetime.now(UTC)
            audit_at = self.state.snapshot().next_daily_audit_utc
            if audit_at is not None and now >= audit_at:
                try:
                    await self._sync_and_analyze(initial=False, daily=True)
                except Exception as error:
                    self.state.set_status(
                        health="DEGRADED",
                        message="00:05-UTC-Audit fehlgeschlagen",
                        last_error=str(error),
                    )

            if self._closed_bar_event.is_set():
                await asyncio.sleep(2)
                self._closed_bar_event.clear()
                try:
                    await self._sync_and_analyze(initial=False)
                except Exception as error:
                    self.state.set_status(
                        health="DEGRADED",
                        message="Bar-Close-REST-Bestaetigung fehlgeschlagen",
                        last_error=str(error),
                    )

            snapshot = self.state.snapshot()
            stale = (
                snapshot.last_stream_update_utc is None
                or (now - snapshot.last_stream_update_utc).total_seconds() > 90
            )
            current_hour = now.replace(minute=0, second=0, microsecond=0)
            if stale:
                self.state.set_status(
                    health="DEGRADED",
                    feed_mode="REST_FALLBACK",
                    message="Stream stale; neue Entries pausiert, REST-Fallback aktiv",
                )
                if now.minute >= 2 and rest_recovery_hour != current_hour:
                    try:
                        await self._sync_and_analyze(initial=False)
                        rest_recovery_hour = current_hour
                    except Exception as error:
                        self.state.set_status(last_error=str(error))
            await asyncio.sleep(self.config.paper_poll_seconds)
