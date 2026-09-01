# DMS-Changelog

## 1.1.0 – 01.09.2026

- Dokumentationsfreeze nach ausdrücklichem Bauauftrag in die Implementierungsphase überführt.
- Genau eine `Startbot.bat` als Windows-Komfortstarter beschlossen; einziger technischer Einstieg bleibt `src/main.py`.
- README und Ordnerregel um verbindliche Sauberkeits-, Build- und Aufräumregeln ergänzt.
- Implementierter V1-Stand für Strategie, Binance-Daten, SQLite, Backtest, 24/7-Paper-Runtime und lokale TypeScript-UI dokumentiert.
- Live-Ausführung bleibt bis zu Paper-Soak, Telegram-, Backup-/Restore-, Account- und Eigentümerfreigabe technisch gesperrt.

## 1.0.0 – 31.08.2026

- `HIXTON-SPEC-1.0` als vollständige normative V1-Strategie festgelegt: Formel, `1h`-Timeframe, Parameter, 400-Bar-Warm-up, Initialzustand, Cross-, Bar-Close- und Next-bar-Regeln.
- Sauber getrennt: implementierbare Projektspezifikation ja, unbelegte Identität mit proprietärem Hersteller-Pine nein.
- Backtestkosten verbindlich auf 15 bp je Seite in der Baseline und 40 bp je Seite im Stressfall festgelegt.
- Long-only, 3×80-USDT-Slots ohne automatisches Compounding und deterministische Slotpriorisierung in Anforderungen, Config und Traceability synchronisiert.
- Stale-Data-, Preisabweichungs-, Tagesverlust-, Drawdown-, Order-Timeout- und Teilfill-Grenzen geschlossen.
- Paper-Soak, Telegram-Alarmierung, dedizierter Bot-Account, localhost-UI, Windows-Service und Backup-/Restore-Retention festgelegt.
- Öffentliches GitHub-Repository bestätigt; fremder Pine-Source ohne Rechte ausgeschlossen, keine Open-Source-Lizenz stillschweigend angenommen.
- Entscheidungslog ohne kritische P0-/P1-Lücke geschlossen und DMS-Freigabegates von späteren Implementierungs-/Testnachweisen getrennt.
- Keine Botimplementierung und keine Backtestergebnisse erzeugt.

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
