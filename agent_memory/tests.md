# Tests and acceptance evidence

## Repository quality gate

`scripts/qa_gate.sh` is the canonical local engineering gate:
1. `python -m compileall -q src`
2. Ruff on `src tests`
3. mypy on `src`
4. full pytest suite
5. UI `npm test`
6. UI TypeScript check
7. UI production build

DMS 12 records the last accepted 0.4.9 baseline as 292 Python tests passed, one opt-in Windows-Vault test skipped, 19 UI tests passed, plus Ruff/mypy/TypeScript/build success. This is historical evidence for that commit, not proof for future modifications; any production patch needs a new run.

## Strategy/domain evidence

- `tests/test_strategy_golden.py`: 1,200-bar independent golden parity for each of ten markets; owner Pine-v6 semantics; batch-vs-bar replay identity; stable position-aware signal IDs; provisional/invalid/gap rejection; deterministic ranking precision.
- `tests/test_trade_policy.py`: CMO/slope/stop/trail behavior, no deferred filtered buy, closed-price stop semantics, isolated/portfolio parity, causal no-future-data behavior.
- `tests/test_coin_profiles.py`: complete V6 ten-coin profiles, strict config/version identity, Paper/backtest/restart exactness, chart signal parity, XRP stop persistence, strategy activation safety.
- allocation/risk/model/config tests cover slot caps, cash/risk behavior and strict config validation.

## Paper/backtest evidence

- `tests/test_paper_engine.py`: no historical startup buy, exactly-once checkpoints/restart recovery, persistent soak thresholds, deterministic slot priority, exits before same-bar entries, no invented cash, settings behavior, strategy migration fail-closed.
- `tests/test_runtime_parity.py`: actual next-open requirement, exact Paper vs shared-portfolio fills/equity, restart-equivalent ledger, provisional-candle behavior, execution-epoch preservation.
- backtest engine/reporting tests cover costs, exchange filters, metrics, report/manifest behavior and reproducibility boundaries.

## USDC migration evidence

- `tests/test_usdc_runtime_migration.py`: common real available history, USDC strategy points, credential namespace continuity, and rejection of legacy USDT Paper DB before mutation.
- Other USDC-review tests ensure historical USDT evidence is not relabeled as USDC.

## Live/preflight evidence

- `tests/test_live_preparation.py` verifies password/session/origin protection, exact 50-USDC request validation, credential handling, read-only account checks and current intentional HTTP 409 fail-closed route.
- Current regression explicitly expects `trial_dispatch_available=False`, `production_submission_accepted=False`, trial `NOT_STARTED`, and no trial/order tables created by a blocked start request.

## Order/exchange evidence

- `tests/test_live_orders.py`: immutable intent identity, concurrent single submit claim, exact 50 quote budget, closed pre-submit gate, fill dedup, timeout/restart query-only recovery, crash after claim without guessed retry, partial/fill-details states, base-fee handling, exact quoteQty, terminal-state monotonicity and legacy schema migration.
- `tests/test_live_exchange.py`: real adapter request shape against fake transport, exact USDC market BUY `quoteOrderQty=50.00`, owned SELL quantity, account/symbol binding, ACK->query->fills, no implicit USDT conversion, corrupted/foreign fill rejection, signed POST body, host/endpoint allowlist, no automatic retry and redacted failures.

## Trial/runtime/reconciliation evidence

- `tests/test_live_trial.py`: exact 50 budget, release gate, one global entitlement, all-ten candidate ranking, stale/incomplete/unhealthy rejection, canonical policy filters, restart/timeout no-rebuy, entry disabling, regular exit, strategy freeze, fee assets, missed exit handling, residual review and USDC profile coverage.
- `tests/test_live_reconciliation_runtime.py`: all ten profiles complete one synthetic round trip using actual adapter parser, Paper decision parity, entry-off does not block owned exit, timeout/restart recovery, account/balance/open-order/stale/locked failure cases, immutable baseline, no inactive/stopped runtime network, BNB fees, unresolved external balance change.

## Visible-session/API/UI evidence

- `tests/test_visible_session.py`: no trading before UI, exact origin, authenticated instance replacement, last-tab/reload grace, stop button, terminal watchdog and unknown-port protection.
- UI/API/chart tests cover server truth, local write protection, chart range/aggregation/provisional semantics and current Live-controller feedback.

## Important unproven items

The existing test suite is predominantly unit/integration with fake HTTP/exchange/account responses for Live execution. It does **not** prove:
- a current authenticated Binance Spot Testnet order round trip;
- a current production Binance 50-USDC order round trip;
- current real-account permissions/IP restriction/balance at the moment of submit;
- a complete current pre-submit market price/filter/spread guard;
- production residual/dust lifecycle;
- complete detection of offsetting manual/foreign trades;
- operator recovery of a real open position after process shutdown.

No development agent or CI test may substitute a real-money order for these acceptance items. Real/Testnet execution must be explicitly operator-initiated from the local application after implementation and safety gates are satisfied.
