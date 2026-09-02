# 13 – Konfiguration und Schemata

## Grundregeln

- Konfiguration ist schema-validiert und versioniert.
- Unbekannte Felder sind Fehler, keine still ignorierten Tippschreibfehler.
- Einheiten stehen im Feldnamen oder Schema.
- Secrets werden nur referenziert.
- Aktivierte Konfiguration hat Hash, Freigabezeit und Owner.
- Strategieänderung und Betriebsänderung sind getrennte Versionen.

## Verbindliche V1-Baseline

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
  version: HIXTON-SPEC-1.0
  normative_spec: DMS/03_STRATEGIE_HIXTON.md
  normative_spec_git_commit: REQUIRED_AT_BUILD
  owner_pine_reference_sha256: 8af8e9a1e6c73dc66307271b7fd1141eaae02bc1fe88e8ba97b96e7a861263dd  # V2-Referenz, nicht aktive V1-Formel
  semantics: dms_v1
  timeframe: 1h
  source: close
  vidya_length: 10
  momentum_length: 20
  post_smoothing_type: sma
  post_smoothing_length: 15
  atr_type: wilder_rma
  atr_length: 200
  band_multiplier: 2.0
  warmup_bars: 400
  initial_trend: down_without_order
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
  compounding: false
  slot_priority: normalized_breakout_desc_then_fixed_coin_order

backtest:
  primary_window_years: 3
  mode: all_ten_isolated  # alternativ single_symbol oder paper_live_mirror
  isolated_starting_usdt_per_symbol: 250.00
  isolated_target_notional_usdt: 250.00
  isolated_compounding: false
  single_symbol: null
  fill_model: next_bar_open
  baseline_fee_bps_per_side: 10
  baseline_spread_bps_per_side: 2
  baseline_slippage_bps_per_side: 3
  stress_fee_bps_per_side: 10
  stress_spread_bps_per_side: 10
  stress_slippage_bps_per_side: 20
  benchmark: buy_and_hold

data:
  store_closed_candles: true
  store_provisional_candle: true
  startup_gap_repair: true
  daily_audit_utc: "00:05"
  missing_bar_policy: halt_symbol
  stream_stale_seconds: 90
  final_bar_grace_seconds: 120

execution:
  live_enabled: false
  order_type: market
  max_price_deviation_bps: 25
  acknowledgement_timeout_seconds: 10
  partial_fill_resolution_seconds: 30
  unknown_order_policy: halt_and_reconcile

risk:
  leverage: 1
  allow_margin: false
  allow_futures: false
  allow_short: false
  max_open_positions: 3
  pause_new_entries_daily_loss_pct: 5
  daily_loss_reference_utc: "00:00"
  global_halt_drawdown_pct: 20
  drawdown_action: halt_without_auto_liquidation

operations:
  paper_soak_min_days: 30
  paper_soak_min_closed_bars_per_symbol: 720
  paper_soak_min_closed_trades: 20
  paper_soak_max_days_when_trade_count_low: 90
  manual_trading_same_account: false
  ui_bind: 127.0.0.1
  alert_primary: local_ui_and_structured_log
  windows_service_after_paper_gate: true
  operational_log_retention_days: 90
  backup_target_outside_git_required: true
  backup_retention_daily: 7
  backup_retention_weekly: 4
  backup_retention_monthly: 12

ui:
  chart_ranges: [today, 1w, 1m, 1y, 3y]
  default_range: 1m
  default_resolution_by_range:
    today: 1h
    1w: 1h
    1m: 1h
    1y: 4h
    3y: 1d
  strategy_signal_resolution: 1h
```

Runtimewerte wie Secret-Referenzen und konkrete Account-ID werden bei der Installation gesetzt. Die fachlichen V1-Defaults oben sind verbindlich und dürfen nicht durch Frameworkdefaults ersetzt werden. Telegram ist nicht erforderlich.

## Strategie-Snapshot

Jedes Signal und jeder Backtest referenziert mindestens:

- Strategie-ID/-Version;
- Git-Commit der normativen Spezifikation;
- Hash der vom Eigentümer bereitgestellten Pine-Referenz;
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
strategy_version: HIXTON-SPEC-1.0
normative_spec_git_commit: VALUE
owner_pine_reference_sha256: null  # historische V1; für V2 verpflichtend der dokumentierte Hash
config_sha256: VALUE
data_snapshot_sha256: VALUE
exchange: VALUE
symbols: [TEN_CONFIRMED_SYMBOLS]
timeframe: 1h
warmup_start_utc: VALUE
report_start_utc: VALUE
report_end_utc: VALUE
starting_usdt_per_symbol: 250.00
run_mode: all_ten_isolated|single_symbol|paper_live_mirror
paper_live_mirror_total_usdt: 240.00
paper_live_mirror_slot_count: 3
paper_live_mirror_target_notional_usdt: 80.00
fee_model: baseline_10bps_per_side
spread_model: baseline_2bps_per_side
slippage_model: baseline_3bps_per_side
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

- fehlender Git-Commit der normativen Strategiequelle;
- weniger/mehr als zehn Märkten im Standard-Batch oder nicht genau einem Markt im Einzelmodus;
- doppeltem Symbol;
- nicht positivem Kapital;
- unbekanntem Timeframe;
- Live ohne Paper-/Freigabestatus;
- Short/Futures/Margin entgegen Strategieprofil;
- fehlender Parameter-/Konfigurationshash;
- ungültiger Zeitzone;
- Geheimnis im Klartextfeld.

## Freigabestatus

Binance Spot, Coinliste, 10×250-USDT-Batch, 250-USDT-Einzeltest, 3×80-USDT-Paperbetrieb, 1h-Strategie, Long-only, kein Compounding, Slotpriorisierung, Kostenbaseline, Market-Order und 00:05-UTC-Audit sind fachlich beschlossen. Live bleibt dennoch bis zu Tests, Secrets, Accountabgleich und Gate D deaktiviert.
