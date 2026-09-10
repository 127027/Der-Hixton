# Storage

## Active runtime databases

### `data/hixton-usdc.sqlite3`
Canonical active USDC data/Paper database from the configured runtime path. It contains market data/metadata and the Paper ledger. Old USDT ledgers are not converted or relabeled; legacy USDT Paper structure is rejected before mutation.

`CandleStore` responsibilities include:
- canonical candles keyed by symbol/open time;
- revision evidence when provider values change;
- persisted Binance symbol rules/filters;
- SQLite integrity checks and exact UTC/decimal conversion.

`PaperStore` responsibilities include durable:
- Paper account cash/high-water/risk state;
- strategy session/version;
- Paper settings (`slot_count`, `target_notional_usdc`, `emergency_stop`);
- positions including strategy/version and V6 entry ATR/highest-close data;
- dust;
- event/fill audit rows;
- per-symbol processing checkpoints;
- soak start/progress/bar counters;
- execution epoch/audit records.

Paper startup is idempotent: initialization creates missing structures/defaults but does not refill an existing account or reset existing positions/history. Checkpoints ensure closed bars are processed exactly once across restart.

### `data/live-preparation.sqlite3`
Separate Live/security/order state; it is not a second Paper account and does not duplicate market candles.

Verified tables created by Live modules:
- `live_preparation_audit`: security/preflight audit actions.
- `signal_trial`: singleton one-shot state, frozen strategy JSON, account, arm time, state, entries flag, buy/sell identities, signal snapshots, entry price/ATR, owned quantity, highest close, completion metadata.
- `trial_intents`: immutable order intent identity/account/symbol/side/strategy/reference/budget/quantity plus durable exchange state.
- `trial_fills`: fills keyed by account + symbol + Binance trade id; exact quantity/price/commission/asset and exact quote quantity migration.
- `trial_order_audit`: order lifecycle audit.
- `trial_account_baseline`: immutable singleton pre-trade account balance baseline used by reconciliation.

Order-journal durability rules:
- intent is persisted before submit;
- `SUBMITTING` is atomically claimed before the single exchange POST;
- timeout/exception becomes unresolved/UNKNOWN and later cycles query by stable client order ID instead of resending;
- terminal exchange totals cannot regress or be silently replaced;
- duplicate fills must be numerically identical or reconciliation stops;
- no raw network/key/secret text is persisted.

Reconciliation storage rules:
- baseline can be captured only with no prior intents, no open orders and no locked balances;
- baseline cannot be overwritten;
- expected balance = baseline + own recorded fills - actual commissions per asset;
- completion is not inferred from local state alone.

## Credential/session storage

Binance HMAC credentials and the local UI password verifier are outside Git in Windows Credential Manager through `WindowsVault`.
- No plaintext file fallback.
- Password is persisted as salt/Scrypt verifier, not plaintext.
- Live browser session authorization is process-local and expires; raw session token is not persisted to the project.

`data/runtime-session.json` is an ignored local process-control record for safe same-installation replacement. It contains a random local control token, not Binance credentials. It is removed only by the matching process instance.

## Backtest artifacts

`backtests/v*/runs/` are immutable/reproducible result bundles containing manifests/metrics/trades/equity/report data as appropriate. They are evidence, not runtime account state. Historical USDT runs retain their original quote identity.

## Backups and ignored state

Downloaded market data, SQLite runtime DBs, local logs, virtualenv, caches, secrets, runtime-session control data and large generated run material are intentionally excluded from Git. DMS requires operational backups outside the active worktree; backup/restore acceptance is a release concern, not a GitHub repository state.

## Storage gaps relevant to the one-shot

- Current `signal_trial` and `trial_account_baseline` are singletons and `SignalTrial.arm()` refuses any existing trial/order history. This preserves first-run evidence but prevents a later manual second trial without a proper archival/cycle migration.
- Residual base quantity after an exchange SELL is not yet modeled as a durable completed-trial dust record. Current mismatch becomes `NEEDS_REVIEW`.
- A complete foreign-order history/checkpoint is not persisted; balance conservation alone does not prove no offsetting manual trades happened between snapshots.
