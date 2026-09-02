# Der Hixton Trading Bot

Der Hixton ist ein lokales Binance-Spot-System mit einer gemeinsamen, deterministischen Strategieengine für Backtest und 24/7-Paperbetrieb. Die aktive Paperstrategie bleibt `HIXTON-SPEC-1.0`; ein Pine-v6-basierter V2-Kandidat wird getrennt unter `backtests/v2` erforscht. Echte Live-Orders bleiben bis zum dokumentierten Live-Gate technisch deaktiviert.

Zentrale Projektablage: `https://github.com/127027/Der-Hixton`

## Schnellstart unter Windows

Im Repository existiert genau ein menschlicher Programmstarter:

```text
Startbot.bat
```

Ein Doppelklick erstellt bei Bedarf die lokale `.venv`, installiert ausschließlich die gepinnten Python-Laufzeitabhängigkeiten und startet Paper-Bot plus UI auf `http://127.0.0.1:8765/`. Die Anwendung besitzt intern weiterhin genau einen technischen Einstiegspunkt: `src/main.py`.

Der erste Start lädt und prüft für alle zehn Märkte drei Jahre `1h`-Daten plus 400 Warm-up-Bars. Währenddessen bleibt die UI sichtbar und zeigt `STARTING` oder `DEGRADED`. Historische Signale werden beim Start niemals als neue Paper-Orders nachgehandelt.

## Was die Anwendung enthält

- Binance Spot für BTC, ETH, BNB, SOL, XRP, ADA, LINK, AVAX, DOT und DOGE gegen USDT.
- `HIXTON-SPEC-1.0`: VIDYA/CMO, SMA-Nachglättung, Wilder-ATR, Bänder und geschlossene `1h`-Bars.
- Vom Eigentümer bereitgestellte Pine-v6-Referenz mit eigenem Hash, Golden-Test und getrenntem V2-Kandidaten; keine stille Umschaltung des Paperbots.
- 24/7-Paper-Ledger mit gemeinsamem Startcash 240 USDT, drei Slots à 80 USDT, Kostenmodell, Not-Aus, Tagesverlustpause, Drawdown-Halt und restartfestem Soak-Nachweis.
- WebSocket-Livestream mit REST-Gap-Recovery, Startup-Prüfung und täglichem Audit um 00:05 UTC.
- Verpasste geschlossene Bars werden nach einem Neustart exakt einmal nachverarbeitet; Soak-Tage, Bars je Coin und abgeschlossene Trades werden dauerhaft in SQLite gezählt und in der bestehenden Systemkarte angezeigt.
- Lokale deutsche UI mit zehn Marktkarten, Positionen, Datenqualität und Candlestick-Charts für Heute, 1 Woche, 1 Monat, 1 Jahr und 3 Jahre.
- Kauf-/Verkaufsmarker aus der nativen `1h`-Strategie; 1 Jahr wird nur zur Anzeige auf `4h`, 3 Jahre auf `1d` aggregiert.
- Backtest: gemeinsames 240-USDT-Spiegelportfolio mit drei festen 80-USDT-Slots, zehn strikt isolierte Läufe à 250 USDT oder ein einzelner Coin à 250 USDT, jeweils Baseline und Stress.
- Backtest v2: dokumentierte Parametersuche, ältere Marktsegmente, Kosten-Stress und Nachbarprüfung. Kandidat 1 bleibt `RESEARCH_ONLY`.
- Unveränderliche Backtest-Runordner mit Manifest, Metriken, Trades, Equity und HTML-Bericht.

## Sichere Grenzen

- `LIVE_DISABLED` ist permanent sichtbar. Es existiert noch kein freigeschalteter privater Binance-Orderadapter.
- Ein positiver Backtest ist keine Gewinngarantie.
- Live benötigt unter anderem 30 bis höchstens 90 Tage Paper-Soak gemäß DMS, mindestens 720 neue Bars je Coin, 20 abgeschlossene Papertrades, sichtbare lokale P1/P2-Alarme, Backup/Restore, einen dedizierten Bot-Account und schriftliche Eigentümerfreigabe. Telegram ist nicht erforderlich.
- Secrets, Datenbanken, Marktdaten, Logs, `.venv` und `node_modules` werden nicht in Git gespeichert.

## Kommandozeile

Alle Befehle laufen über denselben Einstieg:

```powershell
py -3 src/main.py status
py -3 src/main.py data sync --symbol ALL
py -3 src/main.py data audit --symbol ALL
py -3 src/main.py backtest all
py -3 src/main.py backtest single --symbol ETHUSDT
py -3 src/main.py backtest portfolio
py -3 src/main.py backtest all --strategy v2
py -3 src/main.py backtest single --strategy v2 --symbol ETHUSDT
py -3 src/main.py backtest portfolio --strategy v2
py -3 src/main.py start --no-browser
py -3 src/main.py live
```

`live` beendet sich absichtlich mit einer Sperrmeldung.

Die Backtestseite besitzt dieselbe eindeutige Auswahl `V1 · aktives Paper` oder `V2 · Forschung` sowie `Gemeinsames 3×80-Portfolio`, `10×250 isoliert` und jeden Einzelcoin. Diese Auswahl ändert niemals die aktive Paperstrategie.

## Entwicklung und Prüfung

```powershell
py -3 -m pip install -e ".[dev]"
py -3 -m pytest -q
py -3 -m ruff check .
py -3 -m mypy src
cd ui
npm.cmd ci
npm.cmd run check
npm.cmd run build
```

UI-Abhängigkeiten sind in `ui/package-lock.json` festgeschrieben. Der gebaute, vom Python-Service ausgelieferte Stand liegt ausschließlich unter `src/hixton/ui/static/`.

## Sauberkeitsregeln

Ordnung und kleine, eindeutige Verantwortungsbereiche sind verbindliche Produktanforderungen:

- Im Hauptordner liegen nur Projektsteuerdateien, `README.md` und die eine `Startbot.bat`.
- Keine Kopien wie `bot_final.py`, `bot_neu.py`, `start_2.bat` oder Coin-spezifische Starter.
- Eine fachliche Backteständerung erhält `backtests/v2`, `v3` usw.; Wiederholungen derselben Methodik erhalten nur eine neue Run-ID unter `backtests/v1/runs/`.
- Laufzeitdaten gehören ausschließlich in ignorierte Ordner wie `data/`, `runtime/`, `logs/` und `backups/`.
- Generierte UI-Dateien liegen nur im vorgesehenen Buildziel; `node_modules` und temporäre Buildreste werden nie eingecheckt.
- Veraltete Dateien werden nicht als `alt`, `old` oder `backup` im Repository geparkt. Git bewahrt die Historie.
- Jede neue Datei benötigt genau eine Verantwortung, den richtigen Zielordner und einen Test oder eine dokumentierte Begründung.
- Vor jedem Commit laufen Python-Tests, Ruff, Mypy, TypeScript-Check und UI-Build.

## Maßgebliche Dokumentation

1. [`DMS/00_DOKUMENTENLENKUNG_UND_START.md`](DMS/00_DOKUMENTENLENKUNG_UND_START.md)
2. [`DMS/03_STRATEGIE_HIXTON.md`](DMS/03_STRATEGIE_HIXTON.md)
3. [`DMS/12_TESTS_ABNAHMEKRITERIEN.md`](DMS/12_TESTS_ABNAHMEKRITERIEN.md)
4. [`DMS/14_BUILD_PLAN_UND_DEFINITION_OF_DONE.md`](DMS/14_BUILD_PLAN_UND_DEFINITION_OF_DONE.md)
5. [`DMS/20_BETRIEBSRUNBOOK.md`](DMS/20_BETRIEBSRUNBOOK.md)
6. [`DMS/23_ORDNERSTRUKTUR_UND_EINSTIEGSPUNKT.md`](DMS/23_ORDNERSTRUKTUR_UND_EINSTIEGSPUNKT.md)
