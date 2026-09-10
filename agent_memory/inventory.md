# Repository inventory

Completeness baseline: the recursive Git tree for `agent/codex-supervisor-v1` at commit `36184a521da19b8a16c586985c8ccef4779e1b18` was retrieved with `recursive=1` and was not truncated. This is the tracked-file baseline for bootstrap; ignored runtime data are intentionally outside it.

## Root/build/operations

- `README.md`: operator-facing current status; 0.4.9 explicitly says one-shot runtime is connected but HTTP start and pre-submit remain blocked.
- `Startbot.bat`: only Windows human starter; creates/uses `.venv`, validates pinned runtime dependencies, requires built UI, delegates to `src/main.py start`.
- `src/main.py`: only technical entry point; delegates to `hixton.cli.main`.
- `pyproject.toml`: Python >=3.11; pinned FastAPI 0.115.5, Uvicorn 0.32.0, websockets 12.0, tzdata 2026.3; dev pytest/mypy/ruff.
- `scripts/qa_gate.sh`: compileall + Ruff + mypy + pytest + UI tests/typecheck/build.
- `.github/workflows/codex-supervisor.yml`: validates committed agent-memory consistency only; no OpenAI secret and no trading execution.
- `config/examples/config.example.json`: canonical secret-free V6-USDC runtime config, ten fixed USDC markets, Paper 250 start / 3×80 baseline, localhost UI, `data/hixton-usdc.sqlite3`.

## Application source

### `src/hixton/domain/`
- `models.py`: immutable candle/indicator/signal/strategy value objects.
- `markets.py`: active quote is strictly USDC; recognizes historical USDT only for persisted-history compatibility.
- `strategy.py`: canonical Hixton VIDYA/CMO/ATR engine, stable signal IDs, canonical entry ranking.
- `trade_policy.py`: shared CMO/slope/stop/trail policy overlay used by Paper/backtests/one-shot.
- `versions.py`: immutable strategy definitions and ten coin profiles; V6 is current Paper-approved USDC strategy.
- `risk.py`: shared 5% UTC-day entry pause and 20% max-drawdown halt for Paper/portfolio mirror.
- `allocation.py`: deterministic slot allocation.

### `src/hixton/data/`
- `binance.py`: public/read-only market data, exchange metadata and 1h kline adapter.
- `storage.py`: SQLite candle/revision/symbol-rule persistence.
- `quality.py`: grid/duplicate/provisional/OHLCV/gap/count/start/end quality audit.
- `sync.py`: incremental gap-aware sync, recent-tail refresh, metadata refresh, final strict audit.

### `src/hixton/runtime/`
- `analysis.py`: rebuilds canonical analyzed points from validated SQLite candles.
- `state.py`: thread-safe runtime snapshots, analyzed points, live provisional candle cache and structured logs.
- `supervisor.py`: startup sync, Paper recovery, websocket + REST recovery, hourly-close processing, 00:05 UTC audit, backtest dispatch, and a separate 2-second one-shot lifecycle tick.

### `src/hixton/paper/`
- `models.py`: Paper account/settings/positions/events/soak/session model.
- `storage.py`: durable Paper SQLite ledger, checkpoints, events, positions, dust, settings, soak and audit.
- `engine.py`: exactly-once new closed-point processing; exits before entries; deterministic ranking; next-real-bar-open model; baseline costs; cash/slot/exchange-filter/risk gates.
- `maintenance.py`: explicit offline fresh-Paper reset only with strong confirmation/archive; not used by normal startup.

### `src/hixton/backtest/`
- `engine.py`: isolated chronological simulation, signal-at-close / next-bar-open execution, exact filters/costs.
- `portfolio.py`: all-ten shared-cash mirror with same ranking/policies/risk and slots.
- `models.py`, `metrics.py`, `reporting.py`: immutable results, metrics and reproducible artifacts.
- `research.py`, `coin_review.py`, `usdc_review.py`: versioned research/USDC review tools; not separate production signal engines.

### `src/hixton/live/`
- `credentials.py`: Windows Credential Manager plus local password/session protection; no file/env fallback.
- `binance.py`: authenticated read-only Binance account/permissions/market readiness check for exact 50 quote test.
- `orders.py`: durable one-shot intent/fill journal and exactly-once submit claim/reconciliation primitives.
- `exchange.py`: actual Binance Spot order transport/adapter, USDC-only market binding, exact BUY `quoteOrderQty=50.00`, explicit owned-quantity SELL, no automatic submit retry.
- `trial.py`: persistent signal-driven singleton one-shot controller.
- `reconciliation.py`: immutable pre-trade balance baseline plus actual-fill balance conservation proof.
- `runtime.py`: 2-second lifecycle driver and final reconciliation handoff.
- `preparation.py`: credential/preflight service and production wiring; currently deliberate fail-closed release gates.

### `src/hixton/ui/`
- `api.py`: localhost FastAPI surface for runtime/Paper/markets/charts/backtests/logs/settings; installs private Live routes.
- `live.py`: password/session-protected Live/preflight routes; one-shot start currently validates exact 50 USDC then returns 409 without arming.
- `chart.py`: chart payload/aggregation and markers.
- `server.py`: local Uvicorn runner; only localhost; visible process lifecycle.
- `lifecycle.py`: no trading before visible UI; browser/terminal lifetime controls; graceful stop without forced liquidation.
- `instance.py`: exclusive local instance reservation and authenticated replacement of same installation only.

## UI source

- `ui/index.html`: overview, charts, positions/events, backtests, quality, system/logs, settings, Binance connection and Live/Test-Trade controls.
- `ui/src/main.ts`: core API polling/rendering/chart/backtest/events/navigation.
- `ui/src/live-preparation.ts`: private Binance/Live interaction and `live-trial-start` flow.
- `ui/src/trading-settings.ts` + `settings-draft.ts`: one shared persisted settings source, dirty-draft blocking and emergency-stop preservation.
- `market-signal.ts`, `session-lifetime.ts`, `styles.css`: display semantics, browser presence, styling.
- `ui/tests/*.mjs`: isolated DOM/controller regressions.
- built `src/hixton/ui/static/**`: generated production UI artifacts, not an independent source of behavior.

## Tests

Tracked Python tests cover domain, strategy golden parity, trade policies, data/storage/quality, allocation/risk, backtest/portfolio/reporting, Paper/maintenance/restart, API/chart/UI, visible-session lifecycle, USDC migration/review and the full offline Live/one-shot stack (`test_live_preparation`, `test_live_orders`, `test_live_exchange`, `test_live_trial`, `test_live_reconciliation_runtime`). See `tests.md`.

## DMS and historical evidence

- `DMS/00`–`23`, changelog/templates: requirements, strategy, risk, data, backtest, orders, UI, architecture, operations, security, tests, config, build, traceability, decisions, results, risk register, runbook, collaboration, external-source notes, structure.
- Current precedence for the one-shot is DEC-055 / application 0.4.9. Older USDT statements are historical unless explicitly retained.
- `backtests/v1`…`v7` contain immutable/curated historical or validation evidence. Generated run artifacts are evidence, not runtime code.
- `strategy/source_material` and `strategy/pine` are reference inputs used by golden tests; no second runtime strategy implementation.

## Ignored runtime data (not tracked baseline)

Databases, downloaded candles, local logs, `.venv`, backups, `runtime-session.json`, keys/passwords, and large generated run directories are runtime/deployment state and intentionally not committed. Secrets are never expected in Git.
