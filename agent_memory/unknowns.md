# Unknowns, gaps and evidence boundaries

## Repository-understanding status

The current tracked repository has been inventoried and the active runtime, strategy, data, Paper, backtest, Live one-shot, storage, API/UI, process lifecycle, tests, build/QA and DMS precedence have been traced through implementations and cross-checked against the latest DMS/README.

No remaining question in this file is merely an unanswered code-navigation question. Items below are either **known implementation gaps** or **external/operator facts that GitHub cannot prove**.

## Known implementation gaps (repository facts)

### G1 — Test Trade start is deliberately disconnected
- `POST /api/live/trial/start` validates exact 50 USDC then always audits blocked + returns 409.
- It does not capture a baseline and does not call `SignalTrial.arm()`.

### G2 — two constant-false production gates
- `SignalTrial.release_check` is injected as `lambda: False`.
- `TrialOrderExecutor.pre_submit` is injected as `lambda _: False`.
- These must become real policy checks; replacing them with constant true would violate DMS 20/DEC-055.

### G3 — no immediately-before-submit executable-price guard
DMS requires <=25 bps deviation from intent reference. Current real exchange adapter has no ticker/book-price call in its transport allowlist and the injected pre-submit gate is false. No production price-deviation computation exists.

### G4 — no fresh dynamic filter/quantity guard immediately before POST
The read-only preflight checks exchangeInfo earlier, but the actual order transport currently does not reload/validate current `LOT_SIZE`, `MARKET_LOT_SIZE`, notional and quote-order rules immediately before the send. Persisted Paper filters are not sufficient proof for real submission.

### G5 — no fresh direct balance/ownership gate at submit
The earlier account preflight can expire/change. A future pre-submit policy must re-check free USDC for BUY and exact test-owned/free base availability for SELL immediately before dispatch without adopting foreign holdings.

### G6 — account baseline exists but is not wired into arming
`TrialReconciler.capture()` is implemented/tested but the public one-shot start path never captures the baseline before creating the entitlement.

### G7 — residual/dust lifecycle incomplete
Current SELL intent attempts the recorded owned quantity. If exact consumption does not equal owned quantity, controller enters `NEEDS_REVIEW`. There is no durable classification of sellable quantized residual versus non-tradable dust and no completed-trial accounting for it.

### G8 — singleton design prevents later explicit manual re-arm
`signal_trial` and `trial_account_baseline` are singleton tables; `SignalTrial.arm()` refuses any existing signal-trial row or any prior order intent. This supports the first one-shot but not the desired "after a fully completed trial, a later new manual button press may create a new independent trial" workflow. Evidence must be archived, not deleted to simulate a fresh start.

### G9 — foreign/manual trade proof is incomplete
Balance conservation catches unexplained net differences but cannot detect offsetting manual trades between snapshots. Current DMS requires either stronger order-history evidence or a specifically accepted isolated bot-account operating contract plus monitoring.

### G10 — Spot Testnet path is not end-to-end configurable
`BinanceSpotTransport` accepts `https://testnet.binance.vision`, but `LivePreparation.connect_runtime()` hard-codes the production host `https://api.binance.com`. `BinanceReadOnlyClient` also hard-codes production `_BASE` and includes SAPI permission inspection. Therefore the current application cannot simply be switched end-to-end to Spot Testnet through the runtime config.

### G11 — UI lacks full real-trial evidence board
Current UI can show high-level trial state/blockers but not complete intent/order/fill/fee/residual/reconciliation/history evidence required for a trustworthy operator acceptance.

### G12 — CLI/status documentation has stale historical wording
Some DMS subsections and CLI status text still describe `live_execution` as not implemented or refer to older USDT/240-USDT states. Current precedence is DEC-055 / 0.4.9 + current code: active runtime is USDC, real adapter/runtime primitives exist but production release remains incomplete. Historical text must not drive new USDT implementation.

## External/operator unknowns (not answerable from GitHub)

- Actual current Binance API-key permissions and IP restriction on the user's account.
- Current free USDC/BNB and presence of foreign balances/open orders at the moment of a future trial.
- Current Binance account/subaccount isolation discipline and whether manual trading is occurring outside the bot.
- Actual exchange latency/spread/slippage during a future order.
- Successful real Spot Testnet round trip using the eventual release candidate.
- Successful production 50-USDC BUY/SELL/reconciliation round trip.
- Real operator restart/recovery behavior while a production position/order is unsettled.
- Whether the separate `GithubAGENT` checkout on the user's Windows laptop passes the complete QA gate after future code changes.

## DMS precedence/cross-check notes

- Latest decision: DEC-055 / application 0.4.9.
- Active quote: USDC. Older `50 USDT`, `3×80 USDT`, `240 USDT` passages are historical unless a newer paragraph explicitly preserves the underlying non-quote-specific rule.
- Active one-shot intent: exactly one **fresh post-arm qualified signal** among ten USDC coins -> one 50-USDC BUY -> no further entry entitlement -> regular same-coin exit -> account reconciliation.
- Paper remains independent and continues its saved slot/cash simulation.
- Full 3×80 production Live is outside this one-shot release.
- A positive backtest/Paper suite or synthetic exchange test is not Binance execution acceptance.

## Safe implementation order after bootstrap

1. Design an evidence-based pre-submit policy and test it entirely with deterministic fake transports/accounts.
2. Add current market metadata + executable price reads and 25-bps guard.
3. Add immediate BUY/SELL balance/ownership checks.
4. Wire immutable baseline capture + manual arming transactionally.
5. Add durable residual/dust accounting and reconciliation semantics.
6. Add cycle/history model if repeated manually authorized trials are required.
7. Extend UI/reporting with server-derived order/fill/reconciliation evidence.
8. Add explicit Testnet mode without weakening production host/key separation.
9. Run full QA locally on the user's `GithubAGENT` checkout.
10. Only after operator Testnet acceptance may production one-shot readiness be reconsidered. The development agent itself never sends the real order.
