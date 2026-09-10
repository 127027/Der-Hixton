# Architecture

## Entry points and process ownership

- Human Windows entry: `Startbot.bat` only.
- Technical Python entry: `src/main.py` only; delegates to `hixton.cli.main()`.
- Standard runtime: `hixton.ui.server.run_local_dashboard()` -> `RuntimeSupervisor` -> FastAPI app.
- The server binds only to loopback and the visible-session layer starts the supervisor only after a valid browser-presence websocket is established.
- Terminal loss, last-tab loss after grace, or explicit UI stop ends the process. No automatic liquidation is performed.

## Layering

1. **Domain (`src/hixton/domain`)**
   - Exchange/UI/storage independent value objects and strategy logic.
   - `StrategyDefinition` is the versioned canonical configuration source.
   - `HixtonStrategy`, `TradePolicyGate`, `entry_priority`, risk and allocation are shared building blocks.

2. **Data (`src/hixton/data`)**
   - Binance public adapter -> validated 1h candles and symbol metadata -> `CandleStore` SQLite.
   - `runtime.analysis.rebuild_analysis()` converts validated candle history into canonical `IndicatorPoint` series.

3. **Runtime (`src/hixton/runtime`)**
   - `RuntimeSupervisor` owns all long-running work and the thread-safe `RuntimeState` snapshot.
   - Startup synchronizes all ten markets, rebuilds analysis, initializes/replays Paper, then maintains websocket + REST recovery.
   - Bar-close synchronization updates the same `RuntimeState.points()` consumed by both Paper and the one-shot trial.
   - One-shot lifecycle runs on a separate 2-second task so signal selection and submit are not delayed until the next hourly bar.

4. **Paper (`src/hixton/paper`)**
   - Separate simulated account/ledger; does not become a Live account.
   - `process_new_closed_points()` uses canonical points, per-coin policy, deterministic ranking, persisted Binance execution rules, shared risk and operator settings.
   - Fill model is actual next available bar open plus modeled baseline costs; this is simulation only.

5. **Backtest (`src/hixton/backtest`)**
   - Same strategy/policy/ranking semantics in isolated and shared-portfolio historical replay.
   - Historical fills are modeled evidence and never imported as live orders/holdings.

6. **Live one-shot (`src/hixton/live`)**
   - `LivePreparation` owns credential/preflight state and constructs the runtime stack.
   - `SignalTrial` owns the persistent one-shot state machine.
   - `OrderJournal` owns immutable intent/order/fill evidence and exactly-once submit claiming.
   - `BinanceSpotExchange` is the real Spot transport adapter.
   - `TrialReconciler` owns the immutable pre-trade balance baseline and post-trade conservation proof.
   - `TrialRuntime` drives `SignalTrial` every two seconds and invokes final reconciliation.
   - Production release is currently intentionally blocked at HTTP arm, controller release and executor pre-submit layers.

7. **API/UI (`src/hixton/ui`, `ui/`)**
   - Public/local read surfaces expose runtime/Paper/markets/charts/backtests/logs.
   - Sensitive Live routes require exact localhost origin/action header plus password-backed session.
   - TypeScript controllers render server truth; button state does not manufacture a server Live state.

## Active strategy/runtime identity

- Active configured strategy: V6 USDC (`HIXTON-V6-COIN-PAPER-1-d57f88ec2e5f`).
- Fixed universe: BTC, ETH, BNB, SOL, XRP, ADA, LINK, AVAX, DOT, DOGE against USDC.
- Trading timeframe: 1h, closed candles only.
- Paper baseline: 250 USDC account, 3 slots × 80 USDC; settings may be changed within server limits but cannot invent cash.
- Planned exceptional one-shot: exactly one manually armed 50-USDC BUY after a new qualified signal, then only the associated regular exit and reconciliation; it is independent of normal Paper positions/fills.

## Runtime lifecycle details

- `RuntimeSupervisor.start()` starts `_run()` and, if wired, `_trial_loop()`.
- `_run()` retries initial sync until valid, then runs websocket stream and watchdog.
- Closed websocket 1h candles trigger REST confirmation/sync before Paper processing.
- `_trial_loop()` calls `_trial_cycle()` every 2 seconds.
- `_trial_cycle()` reads shared Paper `emergency_stop` as an entry-only permission, then calls `TrialRuntime.tick(state.points(), health, entries_allowed)`.
- An inactive trial causes no credential/account network calls.
- Trial exceptions are reduced to fixed review codes, not raw secret/provider text.

## Important architectural gaps before production one-shot release

- The final pre-submit safety policy is not implemented: current injected executor gate is constant false.
- Controller release is constant false and HTTP start does not establish baseline or arm.
- Current account conservation proof cannot by itself detect offsetting manual trades between snapshots; account isolation or fuller order-history evidence remains required.
- Current singleton trial/order-history design intentionally permits only one lifetime trial; a later repeated manual re-arm requires an explicit cycle/archive design rather than deleting evidence.
- Live SELL/residual handling still assumes an exact owned quantity and treats non-exact completion as review; tradable residual vs non-tradable dust needs a durable model before claiming a completed round trip.
