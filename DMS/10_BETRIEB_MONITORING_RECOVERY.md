# 10 – Betrieb, Monitoring und Recovery

## Systemzustände

| Zustand | Bedeutung | Tradingverhalten |
|---|---|---|
| `STARTING` | Prüfungen laufen | keine neuen Orders |
| `HEALTHY` | alle kritischen Komponenten grün | gemäß aktivem Modus |
| `DEGRADED` | Teilfunktion gestört, Sichtbarkeit vorhanden | neue Entries standardmäßig pausiert |
| `HALTED` | Sicherheit/Zustand unklar oder Not-Aus | keine neuen Orders |
| `STOPPING` | geordnetes Herunterfahren | keine neuen Orders, Checkpoint |

Einzelne Symbole können separat pausiert sein, während andere gesund bleiben. Ein globaler Datenbank- oder Kontosyncfehler stoppt alle Live-Entries.

## Geplanter Betrieb

### Beim Prozessstart

- Startup-Sequenz aus Dokument 05;
- Scheduler-Jobs registrieren;
- überfällige Jobs erkennen;
- Stream verbinden;
- Bar-Close-Verarbeitung aktivieren;
- Paper-/Live-Reconciliation durchführen;
- Health-Report und Startup-Audit schreiben.

### Laufende Jobs

| Job | Takt |
|---|---|
| Livefeed/Bar-Finalisierung | kontinuierlich / je Bar-Close |
| Freshness-Watchdog | deutlich häufiger als ein Trading-Bar |
| Order-Reconciliation | ereignisgetrieben plus periodisch |
| Mitternachts-Datenaudit | täglich 00:05 UTC (`ANNAHME`) |
| Backup | täglich nach erfolgreichem Datenaudit (`ANNAHME`) |
| ausführlicher Datenintegritätscheck | wöchentlich |
| Backtest-Neulauf | manuell/freigegeben oder nach versionierter Daten-/Strategieänderung |

Das Papersystem ist für 24/7-Betrieb vorgesehen. Schlafmodus, Windows-Updates, Internet-/Stromausfall und Service-Autostart werden deshalb im Soak-Test ausdrücklich geprüft. Nach jedem Ausfall gilt Gap-Fill und Reconciliation vor neuer Signalverarbeitung.

Ein Backtest wird nicht ungeprüft jeden Tag automatisch zum Live-Entscheider. Neue Ergebnisse müssen gesichtet und freigegeben werden.

## Health Checks

Pflichtprüfungen:

- Prozess erreichbar;
- Datenbank les-/schreibbar und Migration aktuell;
- letzte geschlossene Kerze pro Symbol erwartungsgemäß;
- Stream verbunden oder Fallback aktiv;
- REST-/Providerzugriff;
- Scheduler letztes/nächstes Ausführungsdatum;
- keine überfällige Reconciliation;
- keine unbekannten Orders/Positionsdifferenzen;
- ausreichend Speicherplatz;
- Systemzeit innerhalb Toleranz;
- letzter Backupstatus;
- aktive Konfiguration gültig und unverändert.

## Logs und Metriken

Jedes Logevent enthält:

- UTC-Zeit;
- Level;
- Komponente;
- Eventcode;
- Korrelations-ID;
- Symbol/Timeframe, falls relevant;
- Modus;
- redigierte strukturierte Details.

Metriken umfassen mindestens Datenlatenz, letzte Barzeit, Lückenanzahl, Stream-Reconnects, API-Fehler, Rate-Limits, Signal-/Intent-/Orderzahlen, blockierte Intents, Filllatenz, Schedulerdauer und Backupalter.

## Alarmklassen

| Priorität | Beispiel | Erwartete Reaktion |
|---|---|---|
| P1 kritisch | unbekannte Live-Order, Kontodifferenz, Datenbankkorruption | Live halt, sofort sichtbar/alarmieren |
| P2 hoch | mehrere fehlende Bars, Stream dauerhaft aus, Backup fehlgeschlagen | Entries pausieren, zeitnah beheben |
| P3 mittel | einzelnes Symbol stale, Rate-Limit-Spitze | Symbol pausieren/überwachen |
| P4 info | täglicher Audit erfolgreich, Backtest fertig | protokollieren |

Benachrichtigungskanal ist noch offen. Die UI allein reicht für unbeaufsichtigten Livebetrieb nicht.

## Sicheres Herunterfahren

- neue Intents stoppen;
- laufende Persistenztransaktionen abschließen;
- offene Börsenorders nicht blind stornieren;
- letzten verarbeiteten Bar-/Event-Checkpoint speichern;
- Status der offenen Orders und Positionen sichern;
- Shutdown-Grund protokollieren.

## Backup

Backup umfasst:

- Datenbank;
- freigegebene Konfigurationen ohne Secrets;
- verschlüsselte/extern verwaltete Secret-Referenzen, nicht Klartext;
- Backtestmanifeste und Berichte;
- Strategiequellen/-hashes und DMS-Version;
- Migrationsstand.

Backups erhalten Prüfsumme, Erstellzeit, Version und Retention. Speicherort darf nicht ausschließlich auf demselben physischen Datenträger liegen (`OFFEN`).

## Restore-Test

Mindestens vor Live-Freigabe und danach regelmäßig:

1. neue isolierte Umgebung bereitstellen;
2. Backupintegrität prüfen;
3. wiederherstellen;
4. Schema/Hashes prüfen;
5. im `LIVE_DISABLED`-Modus starten;
6. Positionen/Orders nicht senden, sondern Reconciliation trocken prüfen;
7. einen bekannten Backtest reproduzieren;
8. Ergebnis und Dauer dokumentieren.

## Typische Recovery-Szenarien

- Strom-/Prozessausfall während Orderübermittlung;
- Streamausfall über mehrere Bars;
- REST-API vorübergehend nicht erreichbar;
- lokale Datenbank gesperrt oder beschädigt;
- historische Kerzen nachträglich korrigiert;
- Börsenfilter geändert;
- Coin delistet/Trading pausiert;
- Systemuhr falsch;
- manuelle Kontobewegung oder Fremdorder;
- Speicherplatz knapp;
- Konfiguration unvollständig.

Für jedes Szenario gilt: Zustand zuerst eindeutig machen, dann fortsetzen. Ungewissheit wird nicht durch eine neue Order „behoben“.
