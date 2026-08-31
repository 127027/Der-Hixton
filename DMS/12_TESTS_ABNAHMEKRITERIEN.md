# 12 – Tests und Abnahmekriterien

## Testebenen

1. Unit-Tests für Mathematik, Zustände, Rundung und Gebühren.
2. Golden-Tests gegen Pine-Referenzwerte.
3. Integrationsprüfungen für Datenprovider, DB und Börsenadapter.
4. Replay-/Backtests mit historischen Bars.
5. End-to-End-Tests der UI bis Ledger/Report.
6. Failure-Injection für Netzwerk, Restart, Teilfill und stale Daten.
7. Paper-Soak-Test über ausreichend viele reale Barwechsel.
8. Sicherheits-, Backup- und Restore-Tests.

## Kritische Strategieprüfungen

- identische VIDYA-/Bandwerte innerhalb definierter Toleranz;
- null Signalabweichungen gegen Pine-Golden-Daten;
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

Konkrete Grenzwerte werden im Testplan festgelegt. Mindestens:

- UI-Anfragen dürfen den Tradingloop nicht blockieren;
- Bar-Close-Verarbeitung endet deutlich vor Beginn der nächsten Bar;
- Backtestlauf und Datenimport zeigen Fortschritt und können kontrolliert abgebrochen werden;
- Logs wachsen unter Retention kontrolliert;
- drei Jahre Chart öffnen innerhalb eines praxistauglichen Zeitfensters;
- Restore ist auf einer sauberen Umgebung reproduzierbar.

## Freigabegates

### Gate A – Strategie eingefroren

- Pine-Datei vorhanden und gehasht;
- Parameter/Timeframe bestätigt;
- Golden-Datensatz vorhanden;
- offene kritische Strategiefragen geschlossen.

### Gate B – Backtest valide

- alle zehn Einzeltests und Portfolio beendet;
- Daten/Kosten/Manifest vollständig;
- Reproduktionslauf identisch;
- Ergebnisse fachlich geprüft, einschließlich Verfehlungen.

### Gate C – Paper bereit

- alle Integrations-, UI- und Failure-Tests grün;
- keine kritischen offenen Defekte;
- Monitoring und Backups aktiv.

### Gate D – Live bereit

- Paper-Soak-Dauer und Mindestanzahl Barwechsel erreicht (`OFFEN`);
- Börse/Account/Keys bestätigt;
- Reconciliation-, Not-Aus- und Restore-Test bestanden;
- Live-Risikolimits bestätigt;
- schriftliche Freigabe des Eigentümers.

## Definition „99 % dokumentiert“

Der Wert ist kein mathematisch exakter Qualitätsbeweis. Für dieses Projekt bedeutet er:

- 100 % der kritischen Anforderungen haben Owner, Status und Test;
- keine kritische Entscheidung steht auf `OFFEN`;
- Pine-Quelle und Börse sind bestätigt;
- alle Annahmen sind bestätigt oder verworfen;
- Traceability besitzt keine kritische Lücke;
- ein unabhängiger Leser kann ohne Strategieerfindung implementieren.

Dieser Zustand ist aktuell wegen der Punkte in Dokument 16 noch nicht erreicht.
