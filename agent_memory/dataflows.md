# Dataflows

## Test Trade / 50-USDC one-shot — verified first pass

### UI to backend

1. `ui/src/live-preparation.ts`
   - Control: `live-trial-start`.
   - Requires authenticated local session, shared settings without blocker, and configured Binance credentials.
   - Sends `POST /api/live/trial/start` with exactly:
     - `confirmation: "TEST 50 USDC"`
     - `quote_asset: "USDC"`
     - `notional_quote: "50.00"`
   - HTTP 409 from `trial/start` is explicitly rendered as "Noch nicht startbereit... Kein Echtgeldauftrag gesendet."

2. `src/hixton/ui/live.py`
   - `start_trial()` validates the exact 50-USDC request.
   - It does **not** call `SignalTrial.arm()`.
   - After validation it obtains status, writes audit event `TRIAL_REQUEST_BLOCKED`, and deliberately returns HTTP 409.
   - This is the first hard blocker preventing any Test Trade from arming.

### Runtime/controller

3. `install_live_routes()` creates `LivePreparation` and calls `service.connect_runtime(supervisor.strategy)`, storing the returned runtime in `supervisor.trial_runtime`.

4. `src/hixton/live/preparation.py::LivePreparation.connect_runtime()` creates:
   - `OrderJournal`
   - deferred Binance spot exchange
   - `TrialOrderExecutor`
   - `SignalTrial`
   - `TrialRuntime`

5. The production wiring is deliberately fail-closed in two additional places:
   - `TrialOrderExecutor(..., lambda _: False)` makes the pre-submit gate reject production submission.
   - `SignalTrial(..., release_check=lambda: False)` makes `SignalTrial.arm()` reject with missing real-money test release.
   - `status()` reports `order_dispatch_available=False`, `ready=False`, `trial_dispatch_available=False`, `production_submission_accepted=False`.

### Signal-driven behavior already implemented offline

`src/hixton/live/trial.py::SignalTrial` already contains a persistent one-shot state machine:
- `arm()` accepts exactly 50 USDC and creates `WAITING_SIGNAL` only after `release_check()`.
- `advance()` waits for real strategy points; it does not invent a signal.
- `_select_entry()` requires the complete strategy universe, closed/tradable/valid bars, freshness <= 90 seconds, post-arm bar, canonical `TradePolicyGate`, an `ENTER_LONG` decision without block reason, positive ATR, and deterministic ranking.
- `_reserve()` atomically reserves the single BUY identity before order construction.
- `_drive_order()` constructs the 50-USDC BUY / owned-quantity SELL, drives the durable order journal, and handles restart/uncertain-order states.
- Exit completion requires account reconciliation; fills alone do not mark the round trip complete.

### Verified root cause for "Test Trade does not execute"

The current behavior is intentional, not a missing signal alone. The Test Trade cannot execute because the production path has **three deliberate release barriers** before a Binance order can be sent:

1. HTTP route always returns 409 and never calls `SignalTrial.arm()`.
2. `SignalTrial.release_check` is hard-wired to `False` in production wiring.
3. `TrialOrderExecutor` pre-submit gate is hard-wired to `False` in production wiring.

Removing only one barrier would still leave the real order path blocked. This matches README 0.4.9, which states that the 50-USDC endpoint remains HTTP 409 and real dispatch is additionally blocked immediately before submit.

## Not yet verified

- Exact supervisor cadence from analyzed points into `TrialRuntime` and restart/error propagation.
- Full Binance market-filter/quantity/price validation path in `exchange.py` and `orders.py`.
- Exact reconciliation ownership and foreign-order checks.
- Relationship between active Paper settings and all Live/Test-Trade gates beyond the UI/status preview.
- Full Backtest/Paper/Live semantic parity.
