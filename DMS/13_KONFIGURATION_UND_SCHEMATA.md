# 13 – Konfiguration und Schemata

## Grundregeln

- Konfiguration ist schema-validiert und versioniert.
- Unbekannte Felder sind Fehler, keine still ignorierten Tippschreibfehler.
- Einheiten stehen im Feldnamen oder Schema.
- Secrets werden nur referenziert.
- Aktivierte Konfiguration hat Hash, Freigabezeit und Owner.
- Strategieänderung und Betriebsänderung sind getrennte Versionen.

## Beispielstruktur – keine finalen Parameter

```yaml
schema_version: 1
environment: paper
timezone_ui: Europe/Berlin

exchange:
  provider: binance
  market_type: spot
  quote_asset: USDT
  api_key_secret_ref: hixton/paper/api_key
  api_secret_secret_ref: hixton/paper/api_secret

strategy:
  id: hixton_vidya_atr
  version: TO_CONFIRM
  pine_sha256: TO_CONFIRM
  timeframe: TO_CONFIRM
  source: TO_CONFIRM
  vidya_length: TO_CONFIRM
  momentum_length: TO_CONFIRM
  post_smoothing_length: TO_CONFIRM
  atr_length: TO_CONFIRM
  band_multiplier: TO_CONFIRM
  evaluate_on_closed_bar_only: true
  position_mode: long_only
  pyramiding: 0

markets:
  - BTC/USDT
  - ETH/USDT
  - BNB/USDT
  - SOL/USDT
  - XRP/USDT
  - ADA/USDT
  - LINK/USDT
  - AVAX/USDT
  - DOT/USDT
  - DOGE/USDT

capital:
  paper_live_total_usdt: 240.00
  paper_live_slot_count: 3
  paper_live_target_notional_usdt: 80.00
  compounding: TO_CONFIRM
  slot_priority: TO_CONFIRM

backtest:
  primary_window_years: 3
  mode: all_ten_isolated  # alternativ single_symbol oder paper_live_mirror
  isolated_starting_usdt_per_symbol: 250.00
  single_symbol: null
  fill_model: next_bar_open
  fee_bps: TO_CONFIRM
  slippage_bps: TO_CONFIRM
  benchmark: buy_and_hold

data:
  store_closed_candles: true
  store_provisional_candle: true
  startup_gap_repair: true
  daily_audit_utc: "00:05"
  missing_bar_policy: halt_symbol

execution:
  live_enabled: false
  order_type: TO_CONFIRM
  max_price_deviation_bps: TO_CONFIRM
  unknown_order_policy: halt_and_reconcile

risk:
  leverage: 1
  allow_margin: false
  allow_futures: false
  allow_short: false
  max_open_positions: 3
  max_daily_loss_usdt: TO_CONFIRM
  max_drawdown_pct: TO_CONFIRM

ui:
  chart_ranges: [today, 1w, 1m, 1y, 3y]
  default_range: 1m
```

`TO_CONFIRM` verhindert absichtlich einen Start. Die spätere Anwendung darf daraus keinen Default ableiten.

## Strategie-Snapshot

Jedes Signal und jeder Backtest referenziert mindestens:

- Strategie-ID/-Version;
- Pine-Hash;
- Parameterhash;
- Timeframe und Quelle;
- Warm-up-Regel;
- Bar-Close-Regel;
- Positionsmodus/Pyramiding;
- Build-/Codeversion.

## Backtest-Run-Manifest

```yaml
run_id: UUID
created_at_utc: ISO-8601
status: valid|invalid|failed|stale
code_version: COMMIT_OR_BUILD_HASH
strategy_version: VALUE
pine_sha256: VALUE
config_sha256: VALUE
data_snapshot_sha256: VALUE
exchange: VALUE
symbols: [TEN_CONFIRMED_SYMBOLS]
timeframe: VALUE
warmup_start_utc: VALUE
report_start_utc: VALUE
report_end_utc: VALUE
starting_usdt_per_symbol: 250.00
run_mode: all_ten_isolated|single_symbol|paper_live_mirror
paper_live_mirror_total_usdt: 240.00
paper_live_mirror_slot_count: 3
paper_live_mirror_target_notional_usdt: 80.00
fee_model: VALUE
slippage_model: VALUE
fill_model: next_bar_open
random_seed: null
runtime:
  os: VALUE
  language: VALUE
  dependency_lock_sha256: VALUE
artifacts:
  data_quality_report: PATH
  trades_csv: PATH
  metrics_json: PATH
  report_html_or_pdf: PATH
```

## Validierung

Start muss fehlschlagen bzw. Live deaktiviert bleiben bei:

- `TO_CONFIRM` in einem für den aktiven Modus nötigen Feld;
- weniger/mehr als zehn Märkten im Standard-Batch oder nicht genau einem Markt im Einzelmodus;
- doppeltem Symbol;
- nicht positivem Kapital;
- unbekanntem Timeframe;
- Live ohne Paper-/Freigabestatus;
- Short/Futures/Margin entgegen Strategieprofil;
- fehlender Pine-/Parameterhash;
- ungültiger Zeitzone;
- Geheimnis im Klartextfeld.

## Beispielwerte sind keine Freigabe

Binance Spot, die zehn Coin-Paare, 10×250-USDT-Backtests, 3×80-USDT-Paperbetrieb und das fehlende feste Gewinnziel sind festgehalten. 00:05 UTC, Long-only, Compounding, Slotpriorisierung, Timeframe und Ordertyp bleiben bis zur Entscheidung ausdrücklich offen bzw. als Annahme markiert.
