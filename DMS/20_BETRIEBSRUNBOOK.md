# 20 – Betriebsrunbook

## Vor jedem ersten Start

1. Modus `BACKTEST` oder `PAPER`; `LIVE` aus.
2. freigegebene DMS-, Strategie- und Konfigurationsversion prüfen.
3. zehn Coins, Börse, Timeframe und Kostenmodell prüfen.
4. Secret-Referenzen testen; keine Werte anzeigen oder kopieren.
5. lokalen Speicherplatz, Systemzeit und Backupziel prüfen.
6. Start auslösen und Startup-Report vollständig abwarten.
7. Nur bei `HEALTHY` Paper-Signalverarbeitung freigeben.

## Täglicher Betreibercheck

- Modus und globaler Healthstatus;
- letzte geschlossene Kerze für alle zehn Coins;
- letzte erfolgreiche 00:05-UTC-Synchronisation;
- offene/ungeklärte Orders;
- Reconciliation- und Saldodifferenzen;
- Datenlücken/Quarantäne;
- Backupstatus;
- P1/P2-Alarme;
- Speicherplatz und Scheduler.

Dieser Check wird im Livebetrieb protokolliert. „Keine Warnung gesehen“ ist kein Ersatz für einen Healthnachweis.

## Geplanter Neustart

1. neue Entries pausieren;
2. offene Orders/Positionen ansehen;
3. Bot geordnet stoppen; Börsenorders nicht blind stornieren;
4. Wartung durchführen;
5. im `LIVE_DISABLED`-/Paper-Zustand starten;
6. Startup-Sync und Reconciliation prüfen;
7. Versionen/Config-Diff kontrollieren;
8. erst danach vorherigen Modus explizit wieder freigeben.

## Stream oder Datenfeed stale

Auslöser: 90 Sekunden ohne Streamupdate oder finale 1h-Bar mehr als 120 Sekunden nach geplantem Schluss nicht verfügbar.

1. betroffene Symbole/Zeitraum feststellen;
2. neue Entries für betroffene Symbole pausiert lassen;
3. REST-/Providerstatus und Systemzeit prüfen;
4. Reconnect abwarten bzw. sicheren Audit starten;
5. fehlende Bars nachladen und Datenqualität erneut prüfen;
6. aktuellen Trendzustand rekonstruieren;
7. keine alten Signale als Live-Order nachholen;
8. bei längerem/mehrfachem Ausfall Incident eröffnen.

## Orderstatus `UNKNOWN`

Auslöser: zehn Sekunden nach Submit keine eindeutige Börsenbestätigung.

1. **keine Ersatzorder senden**;
2. Client-Order-ID bei Börse abfragen;
3. offene/geschlossene Orders und Trades seit Signalzeit prüfen;
4. freie/gesperrte Salden abgleichen;
5. Fills ins Ledger übernehmen, falls eindeutig;
6. bei Restunsicherheit `HALTED` lassen und Incident eskalieren;
7. nur nach dokumentierter Reconciliation entsperren.

Ein nach 30 Sekunden verbleibender Teilfill-Rest wird nach Statusklärung storniert, sofern die Börse ihn als stornierbar meldet. Kein automatischer Ersatzsubmit. Ein Rest unter Börsenminimum bleibt sichtbar als `DUST`.

## Tagesverlust oder Drawdown-Grenze

- Bei 5 % Nettoverlust gegenüber der Equity um 00:00 UTC werden neue Entries bis zum nächsten UTC-Tag pausiert; Exits und Überwachung bleiben aktiv.
- Bei 20 % Drawdown vom globalen Equity-High-Water-Mark wechselt das System auf `HALTED`.
- Keine der beiden Grenzen liquidiert Positionen automatisch.
- Vor manueller Wiederaufnahme nach Drawdown: Ursachen-, Ledger-, Daten- und Konfigurationsprüfung, Incidentabschluss und ausdrückliche Eigentümerfreigabe.

## Telegram-Kanal gestört

1. Fehler in UI und Log sichtbar machen;
2. bei Liveausfall über fünf Minuten `DEGRADED` setzen und neue Entries pausieren;
3. Token/Ziel nur über Secret-Referenz prüfen, nie ausgeben;
4. Testalarm senden und Empfang bestätigen;
5. erst danach Entries wieder freigeben.

## Positions-/Saldodifferenz

1. Live-Entries global pausieren;
2. lokale Fills/Ledger mit Börsentrades vergleichen;
3. manuelle Orders, Gebührenassets, Transfers und Rundungsreste prüfen;
4. keine lokalen Werte ohne Gegenbuchung überschreiben;
5. Ursache und Korrektur auditieren;
6. Reconciliation-Test wiederholen;
7. Eigentümerfreigabe bei Kapitalauswirkung.

## Not-Aus

1. Not-Aus aktivieren; dies verhindert neue Entries.
2. offene Orders und Positionen getrennt beurteilen.
3. Not-Aus darf Positionen nicht still automatisch liquidieren.
4. Falls Schließen nötig: Symbol, Menge, erwartete Kosten und Preisabweichung prüfen; separate Aktion bestätigen.
5. Grund/Actor/Zeit auditieren.
6. Reaktivierung erst nach Ursachenklärung und Reconciliation.

## Delisting/Handelspause

1. Symbol auf `HALTED` setzen;
2. Börsenstatus und bestehende Position prüfen;
3. keine automatische Ersatzkryptowährung wählen;
4. Ausstiegs-/Transferoptionen durch Eigentümer entscheiden;
5. Universumsänderung als neue Strategie-/Konfigurationsversion behandeln;
6. betroffene Backtests neu ausführen.

## Fehlgeschlagener Mitternachtsjob

1. Fehlerursache und betroffene Coins aus Jobbericht lesen;
2. Datenfrische und letzte geschlossene Bar prüfen;
3. sicheren manuellen Audit erneut starten;
4. Idempotenzbericht prüfen;
5. bei historischen Änderungen Backtests `STALE` belassen;
6. bei Wiederholung P2/P1-Incident eröffnen.

## Speicher knapp oder Datenbankfehler

1. Trading auf `HALTED`/Entries pausieren;
2. keine Datenbankdatei im laufenden Betrieb manuell löschen/verschieben;
3. Backup- und Integritystatus prüfen;
4. Logs gemäß dokumentierter Retention rotieren, nicht Audit-/Runartefakte entfernen;
5. bei Korruption Restore-Prozess in isolierter Umgebung ausführen;
6. vor Wiederaufnahme Backtest-Reproduktion und Reconciliation durchführen.

## Restore

1. Zielumgebung isolieren und `LIVE_DISABLED` erzwingen.
2. Backuphash prüfen.
3. DB, Migrationen, Config und Artefakte wiederherstellen.
4. Secrets separat und least-privilege einrichten.
5. Startup-Datenprüfung ausführen.
6. bekannten Backtest reproduzieren.
7. Börsen-Reconciliation trocken durchführen.
8. Restore-Bericht prüfen und schriftlich freigeben.

## Incidentabschluss

- Ursache verstanden;
- Kapital-/Orderauswirkung vollständig abgeglichen;
- Daten/Backtests bei Bedarf neu versioniert;
- dauerhafte Korrektur getestet;
- Monitoring/Test ergänzt;
- Runbook/DMS aktualisiert;
- Owner schließt Incident nachvollziehbar.
