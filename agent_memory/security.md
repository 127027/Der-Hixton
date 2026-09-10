# Security and real-money boundaries

## Local UI/session boundary

`src/hixton/ui/live.py` requires both:
- exact localhost origin matching the current base URL plus `X-Hixton-Action: local-ui-v1`;
- an authorized password-backed session for protected Live actions.

FastAPI also uses `TrustedHostMiddleware` for only `127.0.0.1`/`localhost`, no permissive CORS, API `Cache-Control: no-store`, restrictive CSP/frame/referrer headers and bounded manual parsing for sensitive payloads.

The local password is not the Binance password. `credentials.py` stores only a salt/Scrypt verifier in Windows Credential Manager and keeps authorized session hashes process-local. Sessions expire after 15 minutes; five failed unlock attempts trigger a process-local 60-second lock.

## Credential boundary

`WindowsVault` is the only production credential store for Binance HMAC credentials and UI password material.
- no plaintext file fallback;
- no repo/env export path;
- only exact Hixton credential targets are accessed;
- secret values are not returned by status APIs;
- key deletion/replacement is blocked while a trial is unsettled.

The active `hixton-usdc.sqlite3` path intentionally keeps the same approved vault namespace as the prior standard Hixton database in the same data directory, avoiding secret copies during USDC migration.

## Read-only Binance preflight

`live/binance.py` performs authenticated inspection without an order method. It verifies, among other things:
- reading enabled;
- Spot trading permission/canTrade;
- IP restriction;
- no withdrawal, margin, futures, transfer/options/portfolio permissions;
- SPOT account type;
- no open orders;
- no locked balances;
- no foreign holdings beyond allowed quote/BNB reserve model;
- at least 60 free USDC for a 50-USDC one-shot plus reserve;
- all ten USDC markets are TRADING, Spot-enabled, MARKET-capable and support quote-order-quantity;
- required LOT_SIZE and MARKET_LOT_SIZE metadata and acceptable minimum notional.

The result is memory-cached for at most 60 seconds and invalidated on credential changes/restart. A green read-only check is not an execution release.

## Order transport boundary

`live/exchange.py::BinanceSpotTransport`:
- accepts only explicit Binance production or Spot-testnet HTTPS hosts;
- disables environment proxies and redirects;
- allowlists only time/order/myTrades/account/openOrders methods needed by the current one-shot stack;
- owns timestamp/recvWindow/signature fields;
- checks Binance clock immediately before private requests when needed;
- uses bounded response sizes/timeouts;
- redacts provider errors to fixed HTTP/code information;
- performs no automatic POST retry.

`BinanceSpotExchange` binds a credential fingerprint and USDC symbol universe. It rejects mismatched account/symbol intent, sends exact 50.00 quote for BUY, explicit owned quantity for SELL, verifies acknowledgement identity, then queries actual order/fills.

## Durable exactly-once protections

`OrderJournal` + `TrialOrderExecutor` provide:
- immutable intent parameters;
- stable deterministic Binance client order ID;
- atomic CREATED -> SUBMITTING claim before the one allowed POST;
- no second POST after timeout/crash/ambiguous reply;
- UNKNOWN/reconciliation instead of guessed success;
- monotonic exchange totals/terminal states;
- fill identity/dedup checks;
- exact quote and actual fee-asset accounting;
- no raw provider exception persistence.

## Trial/controller protections

`SignalTrial` provides:
- exactly 50 USDC BUY only;
- one currently persistent global entitlement;
- no immediate/fake signal on arm;
- complete/fresh/closed/valid ten-market data gate;
- post-arm signal requirement;
- frozen strategy/profile identity;
- canonical policy/ranking;
- atomic order reservation;
- entries disabled after BUY while owned exit remains managed;
- test-owned quantity only for SELL;
- explicit final reconciliation before COMPLETED.

## Account reconciliation

`TrialReconciler` captures an immutable pre-trade account baseline only before any intent, with no open orders/locked balances. Post-exit it reconstructs balances from baseline plus own recorded fills minus actual fees.

`read_account_snapshot()` reads account balances on both sides of openOrders and rejects a moving snapshot. Final completion requires no unresolved intents/open orders/locked balances, correct account identity, exact expected balances and zero remaining owned base movement.

Known limitation: balance conservation cannot prove absence of offsetting manual trades between snapshots. DMS therefore requires isolated bot-account discipline and/or fuller order-history evidence before production acceptance.

## Process/lifecycle protections

The bot does not trade before a visible UI connection. Closing terminal or last UI tab stops the process after the defined grace; a later instance replaces only an authenticated same-installation predecessor. Unknown port users are never killed.

Shutdown blocks further cycles and never blindly liquidates/cancels. This creates an operational responsibility: a real open Binance position is unmonitored while the process is off and must be reconciled on restart.

## Current production-dispatch barriers

The repository intentionally prevents a real one-shot from reaching Binance:
1. `/api/live/trial/start` validates but never calls `SignalTrial.arm()`, audits `TRIAL_REQUEST_BLOCKED`, returns HTTP 409.
2. `LivePreparation.connect_runtime()` injects controller `release_check=lambda: False`.
3. It also injects executor `pre_submit=lambda _: False`.
4. status advertises dispatch/readiness as false.

These barriers must be replaced by real evidence-based guards, never by constant true or a UI boolean.

## Remaining engineering requirements before an operator can safely test

Repository-visible missing controls:
- dynamic immediately-before-submit refresh/validation of market filters and executable market price;
- DMS 25-bps deviation guard against the frozen signal reference;
- direct fresh free-USDC / own-base availability checks at submit time;
- baseline capture wired atomically to manual arming;
- durable tradable-residual vs non-tradable-dust lifecycle;
- stronger detection of foreign/manual order activity or explicit isolated-account acceptance;
- server-derived UI evidence for intent/order/fills/residual/reconciliation.

External/operator evidence still cannot be established from GitHub:
- current real key permissions/IP configuration;
- Binance Spot Testnet round trip and failure drills;
- production-account 50-USDC round trip.

The development agent and CI must never send a real Binance order. The code may be prepared for operator-triggered execution, but only a later explicit local user action may create the entitlement.
