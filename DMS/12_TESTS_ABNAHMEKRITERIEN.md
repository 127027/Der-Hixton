# 12 – Tests und Abnahmekriterien

## Testebenen

1. Unit-Tests für Mathematik, Zustände, Rundung und Gebühren.
2. Golden-Tests gegen unabhängig berechnete Werte aus `HIXTON-SPEC-1.0` für V1 und gegen die gehashte Eigentümer-Pine-Semantik für V2;
3. Integrationsprüfungen für Datenprovider, DB und Börsenadapter.
4. Replay-/Backtests mit historischen Bars.
5. End-to-End-Tests der UI bis Ledger/Report.
6. Failure-Injection für Netzwerk, Restart, Teilfill und stale Daten.
7. Paper-Soak-Test über ausreichend viele reale Barwechsel.
8. Sicherheits-, Backup- und Restore-Tests.

## Kritische Strategieprüfungen

- identische VIDYA-/Bandwerte innerhalb definierter Toleranz;
- null Signalabweichungen gegen Spezifikations-Golden-Daten;
- Signal erst nach Bar-Close;
- kein Signal auf Warm-up-/`na`-Bars;
- genau ein Flip-Event pro tatsächlichem Zustandswechsel;
- kein Pyramiding bei wiederholtem Up-Zustand;
- Down-Flip schließt Long im Long-only-Modus;
- Batch und inkrementelles Replay ergeben identische Resultate;
- Neustart an beliebiger Bar ändert Folgesignale nicht.

## Kritische Datenprüfungen

- drei Jahre plus Warm-up für alle zehn Paare;
- Lücke wird erkannt und blockiert das betroffene Symbol;
- Duplikat mit abweichenden Werten wird nicht still akzeptiert;
- offene Kerze bleibt vorläufig;
- Reconnect lädt fehlende Bars nach;
- Mitternachtsjob ist idempotent;
- Datenrevision markiert abhängige Backtests als stale;
- Zeitumstellung Europe/Berlin verändert UTC-Strategie nicht;
- Heute/1W/1M/1J/3J liefern korrekte Grenzen.

## Backtestprüfungen

- Standard-Batch startet zehn isolierte Tests mit exakt 250 USDT je Coin;
- Einzelmodus startet genau den gewählten Coin, zum Beispiel ETH, mit 250 USDT;
- Batchvergleich summiert 2.500 USDT nur rechnerisch und vermischt die zehn Cashbestände nicht;
- Paper-/Live-Spiegellauf startet mit 240 USDT und höchstens drei Slots à 80 USDT;
- bei mehr Signalen als Slots ist die freigegebene Priorisierung deterministisch;
- Next-bar-Fill ohne Look-ahead;
- Gebühren/Slippage auf Ein- und Ausstieg korrekt;
- Tick-/Step-Rundung und Mindestnotional korrekt;
- offene Endposition wird klar mark-to-market bewertet und nicht als heimlicher Fill geschlossen;
- Metriken gegen kleine handgerechnete Fixtures;
- identischer Run erzeugt identische Hashes und Ergebnisse;
- schlechter Coin und Verlusttrade bleiben im Bericht;
- Zielstatus basiert auf Netto-, nicht Bruttoergebnis.

V5-Forschungsnachweise in `tests/test_trade_policy.py`: Identitätsregel verändert weder Einzel- noch Portfolioergebnis; gefilterte Käufe werden nicht auf späteren grünen Bars nachgeholt; Stops reagieren nur auf Schlusskurse, nicht auf Dochte; Steigung verwendet ausschließlich vergangene VIDYA-Werte; zukünftige Kerzen verändern keine vergangenen Fills; Float-Screen/Decimal-Finalist sowie Einzel-/Portfolioentscheidung stimmen auf kontrollierten Fixtures überein. Nichttriviale Forschungsregeln benötigen ausdrücklich eine `HIXTON-V5-…`-Kennung und dürfen sich nicht als aktive V2 ausgeben. Diese Tests ersetzen keinen Paper-Nachweis der Forschungsregeln.

## Execution-/Recovery-Prüfungen

- Retry nach Timeout erzeugt keine Doppelorder;
- unbekannter Submit-Status führt zu Reconciliation;
- Teilfills ergeben korrekte Position/Gebühr;
- Restart zwischen Submit und Response wird sicher aufgelöst;
- Fremdorder/Saldoabweichung stoppt Live-Entries;
- Not-Aus verhindert neue Entries;
- manuelles „alle schließen“ kann nicht versehentlich durch eine einfache Navigation ausgelöst werden;
- Rate-Limit wird eingehalten;
- stale Feed stoppt Entry.

## UI-Abnahme

- alle zehn Karten sichtbar und korrekt zuordenbar;
- Modus und Health permanent sichtbar;
- Chartzeiträume entsprechen definierter Semantik;
- vorläufige Kerze klar markiert;
- Signal- und Fillmarker sind unterscheidbar;
- Backtest zeigt Zeitraum, Kosten und Hashes;
- „unbekannt“ wird nicht als 0 dargestellt;
- Fehlerzustände bieten klare nächste Schritte;
- Einstellungen zeigen Diff und erzeugen Audit;
- Tastaturbedienung, Kontrast und responsive Kernansicht werden geprüft.

## Nichtfunktionale Kriterien

Verbindliche Grenzwerte auf der dokumentierten Referenzinstallation mit zehn Märkten:

- UI-/Lese-API p95 höchstens 2 Sekunden; sie darf den Tradingloop nie synchron blockieren;
- Verarbeitung eines 1h-Bar-Close für alle zehn Märkte einschließlich Persistenz höchstens 60 Sekunden;
- ein kontrollierter Abbruch von Backtest/Datenimport wird spätestens nach 5 Sekunden quittiert und hinterlässt einen eindeutigen Status;
- 3-Jahres-Chart p95 höchstens 3 Sekunden nach verfügbarer lokaler Historie und serverseitiger Aggregation;
- Retention hält normale Betriebslogs bei höchstens 90 Tagen, ohne Audit-/Trade-/Backtestnachweise zu löschen;
- Restore ist in einer sauberen Umgebung reproduzierbar und wird vor Live sowie vierteljährlich nachgewiesen.

## Automatisierter Nachweisstand vom 02.09.2026

- `pytest`: 68 von 68 Tests bestanden, einschließlich versionierter Ledger-Migration, Fail-closed-Strategiekonflikt, Mehrfachslot-Allokation, Aktivierungssperre der verworfenen V3 und Websocket-Health-Recovery ohne Verdecken fremder Fehler;
- Ruff: keine Lint-/Sauberkeitsabweichung;
- mypy: keine Typfehler in 34 Source-Dateien;
- TypeScript: `tsc --noEmit` bestanden;
- npm Audit: 0 bekannte Schwachstellen in 67 Abhängigkeiten;
- Datenqualität: zehn von zehn Märkten mit drei Jahren plus 400 Warm-up-Bars ohne Lücke;
- Backtest: 10×250-USDT-Batch, ETH-Einzelmodus und gemeinsames 3×80-USDT-Portfolio einschließlich risikogleichem Paper-/Live-Spiegel ausgeführt;
- Reproduktion: Metrik-, Trade- und Equity-Dateien bytegleich;
- Browsermatrix: 10 Coins × 5 Zeiträume ohne fehlgeschlagene Chartabfrage geprüft;
- responsive Kernansicht, System-/Log-, Backtest-, Qualitäts-, Einstellungs- und Dokumentationsseite lokal abgenommen.

Diese Nachweise schließen Gate A und Gate B für V1 und V2. Restart-Checkpoint, Nachverarbeitung verpasster Bars, kontrollierter V1→V2-Wechsel, Strategiekonflikt-Sperre und persistente Soak-Zähler sind automatisiert geprüft. Sie ersetzen nicht die noch offenen Gate-C-Nachweise für Backup/Restore, vollständige Failure-Injection und den real ablaufenden V2-Paper-Soak. V3 ist nach dem negativen Mehrfachslot-Risikospiegel verworfen.

## Freigabegates

### Gate A – DMS/Strategie eingefroren

- `HIXTON-SPEC-1.0` ist als normative Referenz vorhanden;
- Formeln, Parameter, `1h`-Timeframe, Warm-up, Initialzustand, Cross- und Fillregeln sind verbindlich;
- Kosten-, Kapital-, Slot- und Long-only-Regeln sind synchron dokumentiert;
- keine kritische Strategieentscheidung steht auf `OFFEN`;
- DMS-Version/Tag und Changelog sind gesetzt.

V1 bleibt durch seine eigene eingefrorene Spezifikation reproduzierbar. Die später vom Eigentümer bereitgestellte Pine-v6-Datei wird zusätzlich für V2 gehasht und per unabhängiger Golden-Implementierung geprüft; sie deutet V1 nicht rückwirkend um.

### Gate B – Backtest valide

- Strategy Engine besteht Golden- und Zustandsmaschinentests ohne Abweichung zur Spezifikation;
- alle zehn Einzeltests und Portfolio beendet;
- Daten/Kosten/Manifest vollständig;
- Reproduktionslauf identisch;
- Ergebnisse fachlich geprüft, einschließlich Verfehlungen.

### Gate C – Paper bereit

- alle Integrations-, UI- und Failure-Tests grün;
- keine kritischen offenen Defekte;
- Monitoring in UI/strukturierten Logs und Backups aktiv;
- dedizierter Bot-Account/Subaccount ohne manuellen Handel vorbereitet.

### Gate D – Live bereit

- mindestens 30 Kalendertage, 720 geschlossene 1h-Bars je Symbol und 20 abgeschlossene Papertrades; bei zu wenigen Trades Verlängerung bis höchstens 90 Tage gemäß DEC-018;
- Börse/Account/Keys bestätigt;
- Reconciliation-, Not-Aus- und Restore-Test bestanden;
- Live-Risikolimits bestätigt;
- schriftliche Freigabe des Eigentümers.

## Definition „99 % dokumentiert“

Ergänzung 05.09.2026: 74 Python-Tests sowie Ruff, mypy (35 Quelldateien), TypeScript und UI-Produktionsbuild bestanden. `tests/test_runtime_parity.py` vergleicht echte Produktionsengines einschließlich Kurslücken, Mengenrundung/Dust, verschiedener Close-Millisekunden und geteilter Restart-Verarbeitung. Zusätzlich geprüft: fehlendes Folge-Open schreibt keinen Checkpoint, die UTC-Grenze innerhalb der ersten zwei Minuten, Fill-/Chart-Zeitraster, vorläufige Kerze ohne neues Signal, Preisfrische und einmaliger Soak-Neustart ohne Positions-/Cash-/Ledgerverlust. Die frühere API-/Browserabnahme hatte die Ausführungslücke nicht erkannt; sie wird nicht als umfassender Paritätsnachweis weiterverwendet. Gate D bleibt offen.

Der Wert ist kein mathematisch exakter Qualitätsbeweis. Für dieses Projekt bedeutet er:

- 100 % der kritischen Anforderungen haben Owner, Status und Test;
- keine kritische Entscheidung steht auf `OFFEN`;
- normative Strategiequelle und Börse sind bestätigt;
- alle Annahmen sind bestätigt oder verworfen;
- Traceability besitzt keine kritische Lücke;
- ein unabhängiger Leser kann ohne Strategieerfindung implementieren.

Dieser Dokumentationszustand ist mit DMS V1.3 erreicht: Die Strategien lassen sich ohne Erfindung implementieren und Dokument 16 enthält keine offene kritische Produktentscheidung. Stand 02.09.2026 bestehen 68 automatisierte Strategie-/Daten-/Backtest-/Paper-/Portfolio-Risiko-/Migration-/Restart-/Recovery-/API-/Charttests, der echte Drei-Jahres-Datenaudit und reproduzierte Backtests. Nach der V2-Aktivierung bestanden alle 50 Coin-/Zeitraumkombinationen die lokale API-Prüfung; Übersicht, Chartbedienung, Signalhistorie, Paper-Ledger und Status wurden zusätzlich im gerenderten Browser geprüft, die Konsole meldete keine Warnung und keinen Fehler. Gate C bleibt bis zu externem Backup-/vollständigen Failure-Nachweisen und dem vorgeschriebenen realen V2-Paper-Soak offen; Gate D bleibt vollständig offen und `LIVE_DISABLED`.
