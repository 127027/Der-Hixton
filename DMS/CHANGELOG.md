# DMS-Changelog

## 0.3.1 – 31.08.2026

- GitHub ausdrücklich als zentrale versionierte Projektablage festgeschrieben; OneDrive ist die lokale Arbeitskopie.
- Frühere Formulierung „Upload erst bei Freigabereife“ entfernt; 99 % bleibt ein separates Releasegate.
- `DEC-029` bestätigt: Slotvergabe nach stärkstem normalisiertem Hixton-Ausbruch mit festem Tie-Break.
- `DEC-030` bestätigt: 80 USDT je Slot bleiben fest bis zu einer bewussten UI-Änderung; kein automatisches Compounding.
- Verbleibende Kernblocker auf Pine-Referenz, Trading-Timeframe und Kostenmodell verdichtet.

## 0.3.0 – 31.08.2026

- `README.md` als einzige zentrale Startdatei festgelegt.
- Einziger späterer technischer Einstieg `src/main.py`; Backtest, Paper, Live und UI werden Modi statt getrennte Startprogramme.
- Reale Repository-Struktur ergänzt.
- Backtests verbindlich unter `backtests/v1`, danach `v2`, `v3`; neue Runs innerhalb einer Methodik überschreiben keine alten Ergebnisse.
- Secret-, Runtime- und Datenpfade über `.gitignore` abgesichert.

## 0.2.0 – 31.08.2026

- Binance Spot als Börse/Datenquelle festgelegt.
- Initiales Universum auf BTC, ETH, BNB, SOL, XRP, ADA, LINK, AVAX, DOT und DOGE gegen USDT festgelegt und aktuelle Binance-Handelbarkeit/Historienlänge geprüft.
- Zwei Systeme getrennt: 24/7 Paper-/Live-Vorbereitung mit 240 USDT und 3×80-USDT-Slots; Backtest-Labor mit 10×250-USDT-Batch und frei wählbarem 250-USDT-Einzeltest.
- Festes 250-/500-USDT-Performanceziel entfernt; Signalparität und ehrliche Nettoperformance getrennt.
- Maximale Nettoperformance als Primärziel, Tradezahl als Sekundärziel dokumentiert.
- GitHub-Repository, Agenten-Branches, Review-, Secret- und späteres Uploadgate dokumentiert.

## 0.1.0 – 31.08.2026

- Eingangsdatei inventarisiert und gehasht.
- Vollständige DMS-Struktur für Scope, Strategie, Märkte, Kapital, Daten, Backtest, Execution, UI, Architektur, Betrieb, Sicherheit, Tests und Konfiguration angelegt.
- Nutzeranforderungen zu zehn Coins, 250-USDT-Einzeltests, drei Jahren, Chartzeiträumen, Startup-Sync und täglichem Update abgebildet.
- Kritische fehlende Quellen und Entscheidungen zentral dokumentiert.
- Risikoregister und konkretes Betriebs-/Recovery-Runbook ergänzt.
- Keine Botimplementierung und keine erfundenen Backtestergebnisse erstellt.
