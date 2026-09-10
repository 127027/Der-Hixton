# Security and real-money boundaries

## Verified first pass: Test Trade safety barriers

### UI/session boundary
- `src/hixton/ui/live.py` requires an exact local UI origin and an authenticated local session before protected Live actions.
- `/api/live/trial/start` accepts only an exact 50-USDC payload and rejects extra fields or other amounts.

### Production-dispatch barriers
The current repository deliberately prevents a real Test Trade from reaching Binance:

1. `/api/live/trial/start` validates the request but never calls `SignalTrial.arm()`; it writes `TRIAL_REQUEST_BLOCKED` and returns HTTP 409.
2. `LivePreparation.connect_runtime()` injects `release_check=lambda: False` into `SignalTrial`; even a direct arm attempt would fail the release gate.
3. `LivePreparation.connect_runtime()` injects `lambda _: False` into `TrialOrderExecutor` as the pre-submit gate; even a reserved intent cannot be productively submitted.
4. `LivePreparation.status()` advertises `order_dispatch_available=False`, `ready=False`, `trial_dispatch_available=False`, and `production_submission_accepted=False`.

### Durable controller safety already present
`src/hixton/live/trial.py` provides verified safeguards in the offline controller path:
- exactly 50 USDC only;
- one global entitlement per durable ledger;
- no immediate/fake signal on arm;
- fresh closed valid bars and canonical `TradePolicyGate` required;
- atomic reservation before order construction;
- restart recovery through durable order identities;
- owned quantity used for exit;
- account reconciliation required before `COMPLETED`.

### Test evidence
`tests/test_live_preparation.py::test_trial_route_is_authenticated_and_fail_closed_without_runtime_adapter` explicitly asserts HTTP 409, `trial_dispatch_available is False`, and `trial.state == NOT_STARTED` for the current public route.

`tests/test_live_trial.py` exercises the controller offline with fake exchanges, including exact 50-USDC budget, single-entitlement concurrency, stale/incomplete/unhealthy signals, canonical filters, restart/timeout recovery, disabling entries, exit/reconciliation, fee handling, residual positions, and USDC symbol/profile behavior.

## Security work still unverified
- Full credential/vault implementation details.
- Binance request signing and transport error redaction.
- Exact market-filter and quantity validation immediately before submit.
- Foreign open-order and residual-balance reconciliation coverage.
- Runtime shutdown/restart behavior while a real position/order is unsettled.
