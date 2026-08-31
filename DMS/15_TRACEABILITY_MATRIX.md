# 15 – Traceability-Matrix

Diese Matrix verhindert, dass eine Anforderung nur im Text existiert, aber später weder gebaut noch geprüft wird.

| Anforderung | Fachquelle | Zielkomponente/UI | Haupttest/Nachweis |
|---|---|---|---|
| STR-001 exakte Hixton-Logik | Pine + DMS 03 | Indicator/Strategy Engine | Golden-Pine-Parität |
| STR-002 nur geschlossene Bars | DMS 03 | Data/Strategy Engine, Chart | Streaming-vs-Batch-Test |
| STR-003 einmaliger Kauf bei Flip-Up | DMS 03 | Strategy Engine | Zustandsmaschinen-Unit-Test |
| STR-004 Down schließt Long | DMS 03 | Strategy/Execution | Szenario flat/long |
| STR-005 Parameter/Warm-up | Pine + Entscheidung | Config/Engine | Config-Schema + Golden-Test |
| STR-006 1.000 Golden-Bars je Testmarkt | DMS 03 | CI/Testartefakt | Abweichungsbericht = 0 Signale |
| STR-007 Signal-Audit | DMS 02/09 | Signal Store/UI | Persistenz-/Drill-down-Test |
| MKT-001 genau zehn Paare | Nutzerauftrag | Config/Dashboard | Schema- und UI-Test |
| MKT-002 Coinliste | Entscheidung ausstehend | Config/Data | Symbolmetadatenprüfung |
| CAP-001 Paper/Live 240 USDT | Nutzerauftrag | Paper-/Live-Ledger, UI | Startsaldo-/Cash-Test |
| CAP-002 drei Slots à 80 USDT | Nutzerauftrag | Portfolio/Execution/UI | Slotlimit- und Notionaltest |
| CAP-003 UI-änderbare Slotgröße | Nutzerauftrag | Settings/Config/Audit | Validierungs-/Vorwärtswirkungstest |
| CAP-004 kein fixes Gewinnziel | Nutzerklärung | Backtestreport | Report enthält Fakten statt Zieloptimierung |
| CAP-005 Slotpriorisierung | Entscheidung ausstehend | Strategy/Portfolio | simultane Signale/volle Slots |
| CAP-006 Nettogewinn vor Tradezahl | Nutzerwunsch + Kostenrealität | Optimierung/Report | Gebühren-/Tradezahlvergleich |
| BKT-008 10×250 USDT | Nutzerauftrag | Backtest Batch | zehn isolierte Ledger-Fixtures |
| BKT-009 Einzeltest 250 USDT | Nutzerauftrag | Backtest UI/Engine | ETH-only-Test ohne andere Coins |
| BKT-010 240-USDT-Spiegellauf | DMS 04/06 | Backtest Portfolio | Parität zu Paper-Slotmodell |
| RSK-001 kein Leverage/Margin/Futures | DMS 04/11 | Config/Execution | Startblockade/Permissionscheck |
| RSK-002 Börsenfilter | DMS 04/07 | Risk/Execution | Tick/Step/Min-Notional-Tests |
| DAT-001 OHLCV persistent | Nutzerauftrag/DMS 05 | DB/Data API | Schema-/Roundtrip-Test |
| DAT-002 Startup-Vollprüfung | Nutzerauftrag | Startup/UI Health | Lücken-/Duplikat-Fixtures |
| DAT-003 inkrementelles Nachladen | Nutzerauftrag | Data Adapter | Paging-/Retry-Test |
| DAT-004 00:05-UTC-Audit | Nutzerauftrag + Annahme | Scheduler/UI | Scheduler-/DST-Test |
| DAT-005 Stream + REST-Fallback | Live-UI-Ziel | Data Adapter | Disconnect-/Recovery-Test |
| DAT-006 offene Kerze vorläufig | DMS 05 | Engine/UI | kein Signal auf provisional |
| DAT-007 lokale 3-Jahres-Historie | Nutzerauftrag | Chart API/UI | Range-/Datenquellentest |
| BKT-001 drei Jahre | Nutzerauftrag | Backtest/Report | Fenstergrenzen-Test |
| BKT-002 Next-bar-Fill | DMS 06 | Backtest Engine | Look-ahead-Negativtest |
| BKT-003 Kosten/Rundung | DMS 06 | Backtest/Execution | handgerechnete Fixtures |
| BKT-004 keine Bias-/synthetischen Preise | DMS 06 | Data/Backtest | Qualitäts- und Code-Review |
| BKT-005 vollständige Metriken | DMS 06 | Report/UI | Snapshot-/Formeltests |
| BKT-006 Run-Manifest | DMS 13 | Artifact Store/UI | Reproduktionslauf |
| EXE-001 getrennte Zustände | DMS 07/09 | Domain/DB/UI | State-machine-Test |
| EXE-002 Idempotency | DMS 07 | Execution | Doppel-Submit-Failure-Test |
| EXE-003 Startup-Reconciliation | DMS 07/10 | Execution/Health | Restart zwischen Submit/Antwort |
| EXE-004 Teilfill/Fehlerzustände | DMS 07 | Execution/Ledger | Adapter-Szenarien |
| EXE-005 Not-Aus | DMS 07/08 | UI/Risk | E2E und Berechtigungstest |
| UI-001 zehn Marktkarten | Nutzerauftrag/DMS 08 | Dashboard | UI-Abnahme |
| UI-002 fünf Chartzeiträume | Nutzerauftrag | Chart UI/API | Grenz-/Zeitzonentest |
| UI-003 Indikatoroverlays | Indikatorbeschreibung | Chart UI | Golden-Screenshot/Datenvergleich |
| UI-004 vorläufige Kerze sichtbar | DMS 08 | Chart UI | Visual-/Semantiktest |
| UI-005 Einheiten/Zeitzone | DMS 08 | gesamte UI | UI-Inventur |
| UI-006 Modusunterscheidung | DMS 01/08 | Header/Settings | E2E Moduswechsel |
| UI-007 Kosten am Backtest | DMS 06/08 | Report UI | Report-Abnahme |
| OPS-001 Health | DMS 10 | Health/API/UI | Komponentenausfalltests |
| OPS-002 strukturierte Logs | DMS 10/11 | Observability | Schema-/Secret-Scan |
| OPS-003 Backup/Restore | DMS 10 | Operations | isolierter Restore-Test |
| SEC-001 keine Secrets | DMS 11 | alle Komponenten | Secret-Scan/Logtest |
| SEC-002 eingeschränkter Key | DMS 11 | Exchange Setup | Berechtigungsnachweis |
| SEC-003 Live-Gates | DMS 12 | Config/UI/Deploy | negativer Freischalttest |
| QLT-001 Traceability | DMS 12/15 | DMS/Testmanagement | Review ohne kritische Lücke |
| COL-001 GitHub-Repository | Nutzerauftrag/DMS 21 | Git/CI/DMS | Remote-/Secret-/Review-Check |

## Pflege

Neue kritische Anforderungen erhalten mindestens einen positiven und einen negativen Test. Ein `OFFEN` in der Fachquelle darf nicht durch einen grünen Implementierungstest kaschiert werden.
