# 20 – Betriebsrunbook

UI-Stand 0.3.2: Nach einem UI-Update die vorhandene Browserseite einmal neu laden (bei altem Bundle `Strg+F5`). Kein Kontoreset nötig. Unter Backtests zuerst Version und Testart wählen; nur der neueste passende Lauf steht direkt sichtbar, frühere Läufe lassen sich aufklappen. Ein historischer RISIKOHALT ist nicht der aktuelle Paper-Healthstatus. Abnahme und unverändert erhaltener V6-Soak: DMS 18.

## Aktuell: V6-Paperexperiment und ausdrücklicher Neuanfang (DEC-045)

DEC-045 (06.09.2026): Auf ausdrücklichen Eigentümerwunsch wird V6 `HIXTON-V6-COIN-PAPER-1-9734f240e873` als **Paper-Experiment** aktiviert. Der frische Modellaccount startet mit 250 USDT, drei 80-USDT-Slots und 10 USDT Anfangsreserve. Alte Paperpositionen, Ereignisse, Dust und Soak bleiben ausschließlich im geprüften lokalen Vollarchiv; sie werden weder als neue Trades noch als Gewinn übernommen. Normale Neustarts erhalten das Konto weiterhin. Die schwächeren jüngsten/älteren Ergebnisse bleiben bestehen; dies ist keine Robustheits-, Optimalitäts- oder Livefreigabe.

### Genau ein Starter, kein automatischer Reset

Normal starten: `Startbot.bat`. Backtestauswahl verändert Paper nicht. Neues Paperkonto nur auf ausdrücklichen Auftrag:

1. `backtests/v6/README.md` einschließlich Verlustfenstern und Risikohalts lesen.
2. Den identifizierten einzelnen Hixton-Prozess stoppen; Port 8765 muss frei sein. Während der Wartung nicht parallel starten.
3. Geprüften Code und V6-Config installieren. Über denselben technischen Einstieg einmalig ausführen:

```powershell
py -3 src/main.py paper-fresh-start --archive backups/paper-v2-archive-20260906/hixton.sqlite3 --confirmation NEUSTART
```

4. Befehl reserviert den UI-Port, sperrt SQLite-Schreibzugriffe, erzeugt ein nicht überschreibbares Vollarchiv, prüft Integrität und SHA-256 und setzt ausschließlich bekannte `paper_*`-Tabellen in einer Transaktion zurück. Ein Fehler beim Reset rollt vollständig zurück; vorhandene Archive werden nie überschrieben. Fehlgeschlagene Archivversuche können eine unvollständige Datei hinterlassen: nicht als gültiges Backup verwenden.
5. Neues Konto: 250 USDT Cash/Startbasis/High-Water-Mark, 3×80, keine Positionen, Trades oder Dust. Audit `PAPER_FRESH_START` enthält Zeitpunkt, Archivpfad/-hash und alte Zeilenzahlen. Das ist keine simulierte Liquidation und keine Gewinnbuchung.
6. `Startbot.bat` starten und Startup-Sync für alle zehn Märkte abwarten. Neue Checkpoints auf letzte geschlossene Bars; Soak startet neu. Alte Signale werden nicht nachgehandelt.
7. `HEALTHY / PAPER / LIVE_DISABLED`, V6-Version, zehn tatsächliche Profile, 250 USDT, drei freie Slots, null alte Paperfills und fünf Chartzeiträume prüfen. Historische Indikatorsignale bleiben für Charts vorhanden.
8. Pfad/Hash/Zeit und Prüfungen in DMS 18 festhalten. Das Archiv bleibt unter ignoriertem `backups/`; Marktdaten bleiben in `data/hixton.sqlite3`.

Für einen späteren Strategiewechsel **ohne** Kontoneuanfang bleibt `paper-activate --strategy v6 --confirmation AKTIVIEREN` ein anderer Wartungsvorgang: Er bewahrt Ledger, Cash und Risikohistorie und modelliert gegebenenfalls alte Positionsschließungen. Nicht mit dem Reset verwechseln.

Historische Abnahme der Anwendung 0.3.0 (`f633f38`) mit unverändertem V2-Konto steht in DMS 18; sie wurde erst durch den neuen ausdrücklichen DEC-045-Auftrag abgelöst.

## Historischer Übergabestand 05.09.2026

Anwendung 0.2.1 läuft auf dem Laptop über die einzige `Startbot.bat`; Strategie bleibt V2, drei Slots à 80 USDT, Live gesperrt. DMS 18 enthält Backup, Neustartnachweis und die beiden frisch aus der UI gestarteten Run-IDs. Der technische Soak startete wegen der Ausführungskorrektur einmalig neu. Alte Positionen und Trades dürfen dafür **nicht** gelöscht oder zu besseren Kursen umgebucht werden.

Neuester Forschungsstand DMS 1.5: V5 untersucht alle zehn Coins einzeln. Zuerst `backtests/v5/README.md` einschließlich Rückschritten und realisiertem/offenem PnL lesen; nicht nur den hohen Dreijahres-Portfolioendwert übernehmen. Forschung über `backtest research --study v5` ändert keine Einstellungen und ist keine neue UI-Strategieauswahl. Keine riskanten Kontoresets oder Soak-Neustarts allein für einen Forschungsbericht. Für eine Fortsetzung durch GPT/Codex sind Versuchskatalog, Rohbericht-Hash, Quell-/Datenhashes und nächste fachliche Schritte im V5-Nachweis festgehalten.

Bei „handelt zu wenig“ zuerst freie Slots, offene Positionen, letzten **neuen** Trendwechsel und den Blockierungsgrund unter Positionen/Orders prüfen. Ein grüner Dauertrend ist kein erneuter Entry; mehrere Slots im selben Coin sind weiterhin nicht freigegeben. Zum Zeitpunkt des Updates waren ADA, DOGE und ETH gleichzeitig offen.

Für eine Verzögerungsprüfung tatsächlichen Verarbeitungszeitpunkt (`/api/paper/events`: `processed_at_utc`) und modellierte Fillzeit (`occurred_at_utc`) getrennt lesen. `LEGACY_CLOSE_OR_MIGRATION` besitzt keinen neuen Latenznachweis. Datenqualität muss die gerade abgeschlossene Stunde zeigen; nach zwei Minuten fehlende Kerzen sind ein Recoveryfall. Modellexits alter Einstiege zählen nicht als vollständige neue Soak-Trades. Der private Orderadapter, Reconciliation und ein realistischer Ausführungs-/Restore-/Störungsnachweis bleiben vor Echtgeld offen.

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

## Kontrollierter Paper-Strategiewechsel

Ein Strategiewechsel ist kein normaler Neustart und erfolgt nie über die Backtestauswahl.

1. ausdrückliche Eigentümerentscheidung und Zielversion im Entscheidungslog prüfen;
2. laufenden Paperprozess geordnet stoppen und lokale SQLite-Datei sichern;
3. Code, Konfiguration, DMS, Golden-Tests und Ziel-Backtests auf denselben Commit bringen;
4. Daten für alle zehn Märkte vollständig synchronisieren und auditieren;
5. einmalig über den einzigen Einstieg `py -3 src/main.py paper-activate --strategy v2 --confirmation AKTIVIEREN` migrieren;
6. kontrollierte Schließungen alter Paperpositionen, Auditdatensatz, neue Strategie-Session, Start-Equity und zurückgesetzten Soak prüfen;
7. Bot ausschließlich in Paper starten; ein Versionskonflikt muss den Start blockieren;
8. Header, Systemkarte, Ledger, zehn Märkte und alle Chartzeiträume prüfen;
9. `LIVE_DISABLED` muss unverändert sichtbar und technisch erzwungen sein.

Die Migration löscht keine alten Ereignisse. Eine Wiederholung auf dieselbe aktive Version ist idempotent. Ein Wechsel zurück benötigt eine neue ausdrückliche Entscheidung; keine Datenbankdatei wird manuell umgeschrieben.

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

## Lokale Alarmanzeige oder Log gestört

1. Botstatus direkt über die lokale Status-API und Datenbank nur lesend prüfen;
2. bei Ausfall der UI **oder** des strukturierten Logs `DEGRADED` setzen und neue Entries pausieren;
3. Ursache in API, Dateisystem, Datenbank und Browserkonsole prüfen;
4. P1-Testereignis auslösen und Sichtbarkeit in UI sowie Log bestätigen;
5. erst danach Entries wieder freigeben.

Telegram ist kein Pflichtbestandteil. Ein später optionaler externer Alarmkanal wird als Zusatz behandelt und darf die lokalen Pflichtnachweise nicht ersetzen.

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
