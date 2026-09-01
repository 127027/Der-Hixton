# 14 – Build-Plan und Definition of Done

Dieses Dokument beschreibt Reihenfolge und tatsächlichen Nachweisstand. Der Eigentümer hat nach dem DMS-Freeze die Implementierung ausdrücklich beauftragt.

## Implementierungsstand am 01.09.2026

| Phase | Technischer Stand | Freigabestatus |
|---|---|---|
| 0 – Spezifikation | DMS V1/`HIXTON-SPEC-1.0` eingefroren | **BESTANDEN** |
| 1 – Strategie-Domain | eine Engine, Golden-/Replay-/Zustandstests | **BESTANDEN** gegen eigene normative Spezifikation; keine unbelegte Herstellerparität |
| 2 – Datenplattform | Binance REST/WebSocket, SQLite-WAL, Revisionen, 00:05-UTC-Scheduler, 10×3 Jahre + Warm-up geprüft | **TECHNISCH BESTANDEN**; echter nächster Mitternachtslauf bleibt Betriebsnachweis |
| 3 – Backtest | 10×250 und Einzeltest, Baseline/Stress, immutable lokale Runs, Reproduktionsvergleich | **BESTANDEN**; Ergebnisstand in DMS 18 |
| 4 – UI-Lesemodus | zehn Märkte, fünf Zeiträume, Overlays, Signal-/Fillmarker, Tabellen, Qualität, Logs | **BESTANDEN** in lokaler Browser-Abnahme |
| 5 – Paper Execution | persistenter 240-USDT-/3×80-Ledger, Slotpriorität, Kosten, Guards, Restart-Checkpoint | **IMPLEMENTIERT**, Gate C/Soak noch nicht bestanden |
| 6 – Live-Adapter | kein privater Orderversand; UI und CLI zeigen `LIVE_DISABLED` | **ABSICHTLICH GESPERRT** |
| 7 – Live-Freigabe | nicht begonnen | **NICHT FREIGEGEBEN** |

## Phase 0 – Spezifikation schließen

- `HIXTON-SPEC-1.0` mit Formeln, Parametern, `1h`-Timeframe, Warm-up und Zustandslogik festlegen;
- Börse, eigener Bot-Account/Subaccount, zehn Paare und Kapitalmodell festlegen;
- Trading-/Ordermodus, Kosten, Risikogrenzen und Betriebsregeln festlegen;
- alle P0-/P1-Entscheidungen schließen und Traceability synchronisieren;
- DMS V1 einfrieren, changeloggen und taggen.

Ergebnis: **mit DMS V1 erreicht**; Implementierung kann ohne Strategieerfindung beginnen, sobald der Eigentümer die nächste Phase beauftragt.

## Phase 1 – Reproduzierbare Strategie-Domain

- Candle-/Decimal-/Zeitmodell;
- VIDYA, ATR, Bänder, Trendzustand;
- Golden-Spezifikationsparität; optionaler Herstellervergleich bei rechtmäßig verfügbarem Source;
- Signal-IDs, Parameterhashes und Unit-Tests.

Definition of Done: Null Signalabweichungen in Golden-Daten, Batch = Replay, keine externe API nötig.

## Phase 2 – Datenplattform

- Provideradapter und Börsenmetadaten;
- historische Downloads für zehn Paare;
- Datenbank, Revisionen und Qualitätsprüfungen;
- Startup-Sync, Stream, Reconnect, täglicher Audit;
- Datenqualitäts-UI/API.

Definition of Done: drei Jahre plus Warm-up pro Paar, Lücken/Fehler nachweislich erkannt, reproduzierbarer Snapshot.

## Phase 3 – Backtest und Reporting

- Eventengine und Next-bar-Fills;
- Gebühren, Slippage, Rundung;
- isolierte 250-USDT-Ledger;
- Standard-Batch 10×250 USDT und frei wählbarer Einzeltest;
- optionaler 240-USDT-Spiegellauf mit drei 80-USDT-Slots;
- Metriken/Benchmarks;
- Manifest und Reports;
- Sensitivität und Holdoutprozess.

Definition of Done: alle zehn Einzeltests und Aggregation exakt reproduzierbar; keine erfundenen Ergebnisse.

## Phase 4 – UI-Lesemodus

- Dashboard mit zehn Karten;
- Chart mit Heute/1W/1M/1J/3J;
- Indikator, Signale, Datenstatus;
- Backtestberichte und Logs;
- klare Empty/Error/Stale-Zustände.

Definition of Done: UI-Abnahmetests bestanden, keine Trading-Schreibfunktion.

## Phase 5 – Paper Execution

- Intent-/Order-/Fill-Zustände;
- Paperadapter und realistisches Fillmodell;
- Positionen/Ledger;
- Not-Aus, Audit, Reconciliation-Simulation;
- Failure-Injection und Soak-Test.
- 24/7-Servicebetrieb mit Binance-Stream, Startup-Recovery und 240-USDT-/3×80-Slotmodell.

Definition of Done: keine Doppelorders in Restart-/Timeouttests; längerer Paperbetrieb ohne kritische Abweichung.

## Phase 6 – Live-Adapter, weiterhin gesperrt

- geringberechtigter Börsenkey;
- Live-Metadaten, Ordermapping und Reconciliation;
- Teilfills, Rate-Limits und Unknown-State;
- Security-, Backup- und Restore-Test;
- Betriebsrunbook und Benachrichtigungen.

Definition of Done: Gate D technisch prüfbar, `live_enabled=false` bleibt Default.

## Phase 7 – kontrollierte Live-Freigabe

- explizite schriftliche Entscheidung;
- kleinster freigegebener Umfang;
- enges Monitoring;
- täglicher Abgleich;
- Review nach festgelegter Beobachtungsphase.

Live-Freigabe ist ein eigener Eigentümerentscheid, nicht automatische Folge eines positiven Backtests.

## Definition of Done für das Gesamtprodukt

- alle P0/P1-Anforderungen implementiert und getestet;
- keine kritischen offenen Entscheidungen;
- Strategieparität belegt;
- Daten für zehn Paare vollständig und aktuell;
- Backtests reproduzierbar;
- UI vollständig gemäß Dokument 08;
- Paper-Soak bestanden;
- Sicherheit, Audit, Not-Aus, Reconciliation, Backup/Restore bestanden;
- Benutzer-/Betriebsdokumentation aktuell;
- bekannte Restrisiken dokumentiert;
- Live bleibt deaktiviert, bis separate Freigabe erfolgt.
