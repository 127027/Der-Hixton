# Der Hixton Trading Bot

Der Hixton ist ein lokales Binance-Spot-System mit einer gemeinsamen, deterministischen Strategieengine für Backtest und 24/7-Paperbetrieb. Aktive Paperstrategie ist seit der ausdrücklichen Eigentümerentscheidung `DEC-037` die V2 `HIXTON-V2-RESEARCH-CANDIDATE-1`; der Name bleibt aus Gründen unveränderlicher Historie bestehen. V1 bleibt vollständig reproduzierbar. Echte Live-Orders bleiben bis zum dokumentierten Live-Gate technisch deaktiviert.

Zentrale Projektablage: `https://github.com/127027/Der-Hixton`

## Schnellstart unter Windows

Prüfstand 05.09.2026 (DMS 1.5): Paper-Ausführung und Charts wurden korrigiert, die aktive V2-Strategie bleibt unverändert. Der [V5-Einzelcoinbericht](backtests/v5/README.md) untersucht nun die Schwächen aller zehn Coins, individuelle Hixton-Filter/Stops und ihre Wirkung auf das gemeinsame Konto. V4 bleibt unveränderte Forschungshistorie. **Noch nicht live-reif.**

Im Repository existiert genau ein menschlicher Programmstarter:

```text
Startbot.bat
```

Ein Doppelklick erstellt bei Bedarf die lokale `.venv`, installiert ausschließlich die gepinnten Python-Laufzeitabhängigkeiten und startet Paper-Bot plus UI auf `http://127.0.0.1:8765/`. Die Anwendung besitzt intern weiterhin genau einen technischen Einstiegspunkt: `src/main.py`.

Der erste Start lädt und prüft für alle zehn Märkte drei Jahre `1h`-Daten plus 400 Warm-up-Bars. Währenddessen bleibt die UI sichtbar und zeigt `STARTING` oder `DEGRADED`. Historische Signale werden beim Start niemals als neue Paper-Orders nachgehandelt. `1m` in der Zeitraumwahl bedeutet **ein Monat**, nicht eine 1-Minuten-Kerze; Strategie und lokaler Rohdatenbestand arbeiten auf `1h`.

## Was die Anwendung enthält

- Binance Spot für BTC, ETH, BNB, SOL, XRP, ADA, LINK, AVAX, DOT und DOGE gegen USDT.
- Versionierte V1- und V2-Strategien: VIDYA/CMO, SMA-Nachglättung, Wilder-ATR, Bänder und ausschließlich geschlossene `1h`-Bars.
- Vom Eigentümer bereitgestellte Pine-v6-Referenz mit eigenem Hash und Golden-Test; der kontrollierte V1→V2-Wechsel bewahrt das alte Ledger und startet einen neuen V2-Soak.
- 24/7-Paper-Ledger mit gemeinsamem Startcash 240 USDT, drei Slots à 80 USDT, Kostenmodell, Not-Aus, Tagesverlustpause, Drawdown-Halt und restartfestem Soak-Nachweis.
- WebSocket-Livestream mit REST-Gap-Recovery, Startup-Prüfung und täglichem Audit um 00:05 UTC.
- Verpasste geschlossene Bars werden nach einem Neustart exakt einmal nachverarbeitet; Soak-Tage, Bars je Coin und abgeschlossene Trades werden dauerhaft in SQLite gezählt und in der bestehenden Systemkarte angezeigt.
- Lokale deutsche UI mit zehn Marktkarten, Positionen, Datenqualität und Candlestick-Charts für Heute, 1 Woche, 1 Monat, 1 Jahr und 3 Jahre.
- Kauf-/Verkaufsmarker aus der nativen `1h`-Strategie; 1 Jahr wird nur zur Anzeige auf `4h`, 3 Jahre auf `1d` aggregiert.
- Backtest: gemeinsames 240-USDT-Spiegelportfolio mit drei festen 80-USDT-Slots und denselben 5-%-/20-%-Risikogates wie Paper, zehn strikt isolierte Läufe à 250 USDT oder ein einzelner Coin à 250 USDT, jeweils Baseline und Stress. Läufe ohne diese Gates heißen ausdrücklich `strategy-only`.
- Backtest v2: dokumentierte Parametersuche, ältere Marktsegmente, Kosten-Stress und Nachbarprüfung; V2 ist für Paper freigegeben, wegen früher Risikohalts aber ausdrücklich nicht für Live.
- Backtest v3: der gewünschte Versuch, mehrere 80-USDT-Slots demselben Coin zu geben, ist getrennt dokumentiert und verworfen; die aktive V2 verteilt höchstens einen Slot je Coin.
- Backtest v4/v5: begrenzte Coin-Parametersuche, Verlustdiagnose, getrennte Trainings-/Prüffenster, Original-Pine-Kontrolle und explizit versionierte Forschungsregeln; keine automatische Paperumschaltung.
- Unveränderliche Backtest-Runordner mit Manifest, Metriken, Trades, Equity und HTML-Bericht.

## Sichere Grenzen

- `LIVE_DISABLED` ist permanent sichtbar. Es existiert noch kein freigeschalteter privater Binance-Orderadapter.
- Ein positiver Backtest ist keine Gewinngarantie.
- Live benötigt unter anderem 30 bis höchstens 90 Tage Paper-Soak gemäß DMS, mindestens 720 neue Bars je Coin, 20 abgeschlossene Papertrades, sichtbare lokale P1/P2-Alarme, Backup/Restore, einen dedizierten Bot-Account und schriftliche Eigentümerfreigabe. Telegram ist nicht erforderlich.
- Secrets, Datenbanken, automatisch geladene `1h`-Marktdaten, Logs, `.venv` und `node_modules` werden nicht in Git gespeichert.

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
py -3 src/main.py backtest portfolio --strategy v3
py -3 src/main.py backtest research --output backtests/v4/runs/mein-neuer-review/research.json
py -3 src/main.py backtest research --study v5 --output backtests/v5/runs/mein-neuer-review/research.json
py -3 src/main.py start --no-browser
py -3 src/main.py live
```

Ohne `--strategy` verwendet ein Backtest automatisch die konfigurierte aktive Paperstrategie V2. V1 und V3 müssen für historische beziehungsweise verworfene Vergleichsläufe ausdrücklich gewählt werden.

`live` beendet sich absichtlich mit einer Sperrmeldung.

`backtest research` verwendet standardmäßig den unveränderten V4-Versuch mit 24 Parametervarianten je Coin. `--study v5` untersucht bis zu 36 Kombinationen je Coin aus drei Hixton-Parameterbasen und zwölf klar beschriebenen Filtern/Stops. Auswahl ausschließlich im Training, danach exakte Einzel-/Portfoliovergleiche. V5 benötigt zusätzlich den im Bericht angegebenen älteren lokalen Datensatz. Beide Studien ändern weder Paperstrategie noch Kontostand; vorhandene Ergebnisdateien werden nicht überschrieben. Bereits betrachtete Prüfdaten werden ausdrücklich nicht als unangetasteter Holdout bezeichnet.

Paper verwendet seit der Ausführungskorrektur `NEXT_BAR_OPEN_V1`: Signal ausschließlich auf geschlossener Kerze, modellierter Fill mit dem tatsächlichen nächsten Kerzen-Open plus Kosten. Der echte Verarbeitungszeitpunkt wird zusätzlich gespeichert. Das ist ein deterministischer Ausführungssimulator, noch kein Nachweis realer Binance-Fills oder realistisch gemessener Orderlatenz. Alte Ereignisse bleiben als Legacy erhalten; der technische Soak startet einmalig neu, Cash und Positionen bleiben bestehen.

Die Backtestseite besitzt die eindeutige Auswahl `V2 · aktives Paper`, `V1 · Historie` oder `V3 · verworfener Mehrfachslot-Test` sowie `Gemeinsames 3×80-Portfolio`, `10×250 isoliert` und jeden Einzelcoin. Diese Auswahl ändert niemals die aktive Paperstrategie.

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
