# Dataflows

## 1. Market data -> analyzed strategy points

`RuntimeSupervisor._synchronous_sync()` is the canonical data path:
1. Binance server time is checked.
2. For all ten fixed USDC symbols, earliest real availability is determined and gaps are synchronized into `CandleStore`.
3. The currently open 1h candle may be stored separately for display/fill reference but is never treated as a closed strategy bar.
4. `rebuild_analysis(..., strategy=self.strategy)` evaluates the frozen active `StrategyDefinition` and per-coin profiles.
5. persisted Binance symbol rules are loaded for Paper/backtest execution constraints.
6. `RuntimeState.replace_analysis(points, quality)` atomically publishes the analyzed series.

Websocket closed-bar events trigger REST confirmation/sync; stale/disconnected stream falls back to REST recovery. Strategy decisions therefore originate from validated closed 1h bars, not directly from arbitrary UI/stream messages.

## 2. Analyzed points -> Paper

At first startup `initialize_paper_at_latest()` creates checkpoints at the latest analyzed close without buying historical signals. On restart it preserves checkpoints and `_process_paper()` replays only newly closed points.

`paper.engine.process_new_closed_points()`:
- groups new closes chronologically;
- requires complete execution-open availability for the slice;
- processes existing-position exits before entries;
- uses canonical `TradePolicyGate` and `entry_priority`;
- applies persisted exchange rules, configured cash/slots, 5% daily entry pause and 20% drawdown halt;
- models fills at the actual next bar open plus baseline fee/spread/slippage;
- atomically persists account, positions, dust, events, checkpoints and soak progress.

Paper is a simulated ledger only. It does not create Binance intents, and its positions/fills are never imported as real ownership.

## 3. UI -> one-shot start request

`ui/src/live-preparation.ts` control `live-trial-start`:
- requires authenticated local session;
- requires saved/clean shared settings and no emergency-stop blocker;
- requires configured Binance credentials;
- POSTs `/api/live/trial/start` with exactly:
  - `confirmation: "TEST 50 USDC"`
  - `quote_asset: "USDC"`
  - `notional_quote: "50.00"`.

Current `src/hixton/ui/live.py::start_trial()` validates the request but deliberately does **not** arm. It audits `TRIAL_REQUEST_BLOCKED` and returns HTTP 409.

## 4. LivePreparation -> runtime stack

At app construction, `install_live_routes()` creates `LivePreparation` and calls `connect_runtime(supervisor.strategy)`. This constructs:
- `OrderJournal(live-preparation.sqlite3)`;
- deferred credential-bound `BinanceSpotExchange`;
- `TrialOrderExecutor`;
- `SignalTrial`;
- `TrialReconciler`;
- `TrialRuntime`, stored as `supervisor.trial_runtime`.

The deferred exchange loads the current credential only on an actual account/order operation. An inactive one-shot therefore performs no credential/account network calls.

Production is currently fail-closed in two additional places:
- `SignalTrial(... release_check=lambda: False)`;
- `TrialOrderExecutor(... pre_submit=lambda _: False)`.

## 5. Supervisor -> TrialRuntime

`RuntimeSupervisor.start()` starts the normal runtime and a separate `hixton-one-shot` task if the trial runtime is wired.

Every 2 seconds `_trial_cycle()`:
1. reads persisted shared settings;
2. converts `emergency_stop` to `entries_allowed=False` without liquidating;
3. passes the same `RuntimeState.points()` used by the application, current UTC time, runtime HEALTHY state and entry permission to `TrialRuntime.tick()`.

This 2-second cycle is deliberate: a newly reserved order can proceed/reconcile without waiting another hour for a strategy candle.

## 6. SignalTrial state machine

`SignalTrial.arm()` currently permits exactly 50 USDC and creates `WAITING_SIGNAL` only after release authorization. It refuses pre-existing trial/order history.

`WAITING_SIGNAL` -> entry selection:
- complete ten-symbol universe required;
- all latest bars share one close boundary;
- latest bar must be closed, valid, tradable and <=90 seconds old;
- close boundary must be after arm time;
- symbol/profile version must match frozen strategy;
- canonical `TradePolicyGate` must emit unblocked `ENTER_LONG`;
- ATR must be positive;
- simultaneous candidates use canonical deterministic ranking.

Winning entry is atomically reserved as `ENTRY_PENDING` with stable trial/order identity before order construction.

`ENTRY_PENDING` -> order driver:
- creates immutable `TrialIntent` for exactly 50 quote units;
- stale/disabled fresh entry is failed before submit;
- release is checked again;
- executor handles single-submit claim or restart reconciliation.

Filled BUY -> `OPEN` with actual average price, net received base, frozen entry ATR/highest-close state and entries disabled.

`OPEN` -> exit selection:
- only the owned symbol is evaluated;
- same coin policy drives flip/stop/trail exit semantics;
- SELL intent uses the test-owned base quantity, never arbitrary Paper/foreign holdings.

SELL -> `AWAITING_RECONCILIATION` only when the consumed amount exactly equals recorded owned quantity; otherwise `NEEDS_REVIEW`.

## 7. Intent -> Binance order/fills

`OrderJournal.create()` persists immutable intent. `TrialOrderExecutor.execute()` calls injected `pre_submit` **before** claiming a new send. If approved:
- journal atomically changes CREATED -> SUBMITTING;
- `BinanceSpotExchange.submit()` sends one MARKET order with stable `newClientOrderId`;
- BUY uses exactly `quoteOrderQty=50.00`; SELL uses explicit base quantity;
- ACK is not treated as a fill: adapter queries `/api/v3/order` and `/api/v3/myTrades`;
- actual executed quantity, exact quoteQty and fees by asset are persisted.

Any ambiguous exception marks the intent unresolved. Later cycles query the stable client ID; they never issue a replacement POST merely because the prior response was lost or Binance reports order-not-found.

## 8. Final account reconciliation

Before the first intent, future production arming must capture `TrialReconciler`'s immutable account baseline. Production route currently does not do this.

After an exit reaches `AWAITING_RECONCILIATION`, `TrialRuntime` reads:
`GET account -> GET openOrders -> GET account`.
The snapshot is rejected if balances changed during that read window.

`TrialReconciler.check()` reconstructs expected balances from:
`baseline + own recorded BUY/SELL fills - actual commission assets`.
Completion requires:
- same account fingerprint;
- no unresolved intents;
- no locked balances;
- no open orders;
- no unexplained asset mismatches;
- no remaining owned base movement.
Only then may `SignalTrial.confirm_reconciled()` set `COMPLETED`.

## 9. Process shutdown/restart

Visible-session termination sets the supervisor stop flag, stops the trial runtime and shuts down the process. It never blindly liquidates or cancels a potentially filled order.

Persistent `signal_trial`, intents and fills survive restart. Pending/unknown intents are queried rather than resubmitted. A real open position would remain on Binance while the program is off, so safe operator restart/reconciliation is mandatory before new entry authorization.

## 10. Verified reason the current Test Trade never executes

Three deliberate production barriers prevent it:
1. HTTP route returns 409 without `arm()`.
2. controller `release_check` is hard-wired false.
3. executor `pre_submit` is hard-wired false.

These are intentional because the following implementation/acceptance work remains:
- dynamic fresh pre-submit market/filter/price/balance/ownership policy;
- baseline capture wired into manual arming;
- durable residual/dust handling;
- stronger foreign/manual-order evidence or accepted isolated-account contract;
- external Testnet/operator acceptance.

Removing a single false/409 is therefore not a valid fix.

## Paper/backtest/live relationship

- Indicator, per-coin profile, `TradePolicyGate` and ranking are shared and parity-tested.
- Paper and portfolio backtest use modeled next-bar-open execution and their own simulated ledgers.
- Live uses the same fresh strategy decision but actual Binance Market fills and a separate real-account reconciliation ledger.
- Exact PnL/fill parity between Paper and Live is neither expected nor claimed; decision parity is the relevant invariant.
