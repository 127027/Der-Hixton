# UI map

## Application shell

Source: `ui/index.html`, behavior mainly `ui/src/main.ts`.

Navigation pages:
- `overview`: runtime banner, Paper equity/cash/free slots/drawdown, ten market cards, manual data sync.
- `chart-panel`: symbol/timezone/range controls, 1h strategy candles with display aggregation (1y=4h, 3y=1d), VIDYA/bands, strategy markers and Paper events.
- `positions`: Paper positions and event table.
- `backtests`: strategy/mode selection, historical-run controls and results.
- `quality`: market history/data-quality table.
- `system`: scheduler/runtime state and structured logs.
- `settings`: shared trade settings, Binance credentials/session, Live/Test-Trade controls.
- `documentation`: version/behavior documentation panel.

Persistent header/status:
- strategy label and health pill are server-derived.
- Paper badge is visible independently of Live state.
- Live state is read from `/api/status` / `/api/live/status`, not inferred from button clicks.

## Core polling/API

`ui/src/main.ts` polls local APIs for:
- `/api/status`
- `/api/markets`
- chart/events/backtest/log surfaces.

The UI uses `X-Hixton-Action: local-ui-v1` for local write actions. Server-side origin checks remain authoritative.

## Shared trading settings

DOM:
- `slot-input`
- `notional-input`
- `settings-button`
- `settings-saved`
- `settings-validation`
- `settings-edit-state`
- `live-plan`

Controller: `ui/src/trading-settings.ts` + `settings-draft.ts`.
- saved settings and unsaved draft are explicitly separated;
- polling cannot overwrite an in-progress draft;
- server limits control max slots;
- saving settings is not consent to start real trading;
- dirty/saving state blocks Live actions;
- a persisted `emergency_stop` is preserved even though its legacy UI toggle is absent.

## Binance/local authorization

DOM:
- `live-auth-panel`
- `live-password`, `live-password-repeat`
- `live-unlock`
- `live-protected`
- `live-key-form`, `live-api-key`, `live-api-secret`, `live-save-key`
- `live-check`
- `live-lock`
- key delete confirmation controls.

Controller: `ui/src/live-preparation.ts`.
- password unlock is separate from Binance key storage;
- sensitive controls remain disabled until authenticated server status;
- secret input fields are cleared after use/page hide;
- credentials are never stored in browser storage;
- `live-check` invokes authenticated read-only Binance account/preflight inspection.

## Live and one-shot controls

DOM:
- `live-state`
- `live-request`: normal/full Live request; currently backend fail-closed.
- `live-off`: entry-only stop; does not force-sell.
- `live-trial-start`: explicit one-shot control.
- `live-trial-status`, `live-trial-result`
- `live-blockers` technical blocker list.

`live-trial-start` flow:
1. require authenticated session;
2. require clean/saved shared settings and no emergency-stop blocker;
3. require configured Binance credentials;
4. POST `trial/start` with exactly `TEST 50 USDC`, `USDC`, `50.00`;
5. current backend returns 409 and UI displays explicit not-ready text.

Current server status reports trial state, blockers and readiness fields. It never turns the Live button green merely because a preflight check succeeded.

## Chart semantics

`src/hixton/ui/chart.py`:
- strategy always trades native closed 1h bars;
- display aggregation only affects chart presentation;
- provisional live candle may be drawn but has no indicator values/signals;
- strategy markers are recomputed with the same `TradePolicyGate` rules;
- Paper fills are distinct from strategy signal markers.

This distinction matters for the one-shot: a green trend or old marker is not permission for a new BUY; the controller needs a fresh post-arm qualified signal.

## Visible-session controls

`ui/src/session-lifetime.ts` opens `/api/session/presence` websocket.
- UI shows connection/stop notice.
- explicit `Bot beenden` sends `stop` and warns that open Binance positions are not sold.
- page hide closes presence; server provides a five-second last-tab grace.
- if a new process instance is detected, UI reloads its current bundle.
- there is no focus/visibility heartbeat that would stop a background but still-open tab.

## UI gap before one-shot release

The current UI has no full real-order lifecycle board for:
- armed-at / selected fresh signal;
- Binance intent/client/order identity;
- submit/unknown/partial-fill states;
- actual fills and fee assets;
- owned residual/dust;
- reconciliation result;
- completed/failed-safe audit history and a later explicit manual re-arm.

These must be server-derived; no UI-only boolean may certify execution or reconciliation.
