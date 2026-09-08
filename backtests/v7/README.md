# V7 – USDC-Migrationsprüfung

Status: **Validierung, nicht aktiviert; keine Echtgeldfreigabe.** Die zehn V6-Coin-Profile werden ohne Optimierung auf echten USDC-Kerzen geprüft. V6-Paper bleibt USDT; historische Zahlen und Konten werden nicht umbenannt. V7 gehört zunächst nicht in die normale aktive UI-Strategieauswahl.

## Festgelegtes Verfahren

- Binance Spot, zehn Coins, 1h, ausschließlich geschlossene Bars, 400 Warm-up-Bars, Signal am Schluss/Fill am nächsten Open.
- Eigene öffentliche USDC-Datenbank `data/usdc-validation.sqlite3`. Keine Schlüssel nötig, keine USDT-Kerzen als Ersatz, keine künstliche Lückenfüllung.
- Angefordert drei Jahre. Tatsächlich gemeinsamer zusammenhängender Zeitraum nach Warm-up aller zehn Coins; spätere Listings/Unterbrechungen werden ausgewiesen. Zusätzlich feste Fenster letzte 365 und 90 Tage, wenn verfügbar.
- Je Fenster zehn Einzeltests à 250 und gemeinsames 250-Portfolio mit 3×80, Baseline und Stress. Aktuelle Börsenfilter statt historisch rekonstruierter Filter; angenommene Kosten statt verifizierter Betreibergebühren.
- USDT-Kontrolle im exakt selben Zeitfenster mit gleicher Strategie und Kosten/Risikoregeln. Bestehende Kerzen ausschließlich lesend, keine Änderung des Paperkontos.
- Die auf USDT erforschten Parameter machen zeitgleiche USDC-Daten nicht zu einem unabhängigen Out-of-sample-Nachweis. Keine Rückoptimierung auf diese Ergebnisse.
- Kanonische unveränderliche Einzel-/Portfolio-Berichte unter `runs/<id>/<fenster>/...`; Kontrolle unter `usdt_same_window_control/`. Manifest nennt Quote, Strategie, Quell-Commit und Kerzenhashes. Gesamtbericht enthält zusätzliche Quellcode-Dateihashes, Datenabdeckung, offene Positionen und realisiertes Ergebnis abgeschlossener Trades.

Aufruf über bestehenden Einstieg: `python src/main.py backtest usdc-review --end 2026-09-08T06:00:00Z --usdt-control-db "PFAD ZUR USDT-DATENBANK"`.

## Noch offen

Währungseindeutige Migration von Runtime, Ledger, UI und Binance-Kontoprüfung; sichere Trennung alter USDT-Historie. Produktiver Orderadapter samt Teilfills/Timeouts/Dust/Restart-Reconciliation und genau einem 50-USDC-Entry. Kontospezifische Handelbarkeit, tatsächliche Gebühren und vollständiger Ein-/Ausstiegsnachweis. Kein automatischer Wechsel auf 3×80 Live.
