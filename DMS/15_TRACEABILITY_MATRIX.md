# 15 – Traceability-Matrix

Diese Matrix verhindert, dass eine Anforderung nur im Text existiert, aber später weder gebaut noch geprüft wird.

| Anforderung | Fachquelle | Zielkomponente/UI | Haupttest/Nachweis |
|---|---|---|---|
| STR-001 exakte Hixton-Logik | DMS 03, `HIXTON-SPEC-1.0` | Indicator/Strategy Engine | Golden-Spezifikationsparität |
| STR-002 nur geschlossene Bars | DMS 03 | Data/Strategy Engine, Chart | Streaming-vs-Batch-Test |
| STR-003 einmaliger Kauf bei Flip-Up | DMS 03 | Strategy Engine | Zustandsmaschinen-Unit-Test |
| STR-004 Down schließt Long | DMS 03 | Strategy/Execution | Szenario flat/long |
| STR-005 Parameter/Warm-up | DMS 03; DEC-001/002/003/011 | Config/Engine | Config-Schema + Golden-Test |
| STR-006 1.000 Golden-Bars je Testmarkt | DMS 03 | CI/Testartefakt | Abweichungsbericht = 0 Signale |
| STR-007 Signal-Audit | DMS 02/09 | Signal Store/UI | Persistenz-/Drill-down-Test |
| STR-008 getrennte V1-/V2-Versionen | DMS 03; DEC-034/036 | Strategy/Config/Backtest/UI | Pine-Golden-Test + keine stille Paperumschaltung |
| MKT-001 genau zehn Paare | Nutzerauftrag | Config/Dashboard | Schema- und UI-Test |
| MKT-002 Coinliste | DMS 04; DEC-005 | Config/Data | Symbolmetadatenprüfung |
| MKT-003 keine automatische Coinrotation | DMS 04/22; DEC-005 | Config/Data/Release | Delisting pausiert statt Ersatz zu wählen |
| CAP-001 Paper/Live 240 USDT | Nutzerauftrag | Paper-/Live-Ledger, UI | Startsaldo-/Cash-Test |
| CAP-002 drei Slots à 80 USDT | Nutzerauftrag | Portfolio/Execution/UI | Slotlimit- und Notionaltest |
| CAP-003 UI-änderbare Slotgröße | Nutzerauftrag | Settings/Config/Audit | Validierungs-/Vorwärtswirkungstest |
| CAP-004 250→500 als Wunsch, nicht Garantie | Nutzerklärung | Backtestreport | Zielerreichung und -verfehlung je Coin sichtbar |
| CAP-005 Slotpriorisierung | DMS 03/04; DEC-029 | Strategy/Portfolio | simultane Signale/volle Slots |
| CAP-006 Nettogewinn vor Tradezahl | Nutzerwunsch + Kostenrealität | Optimierung/Report | Gebühren-/Tradezahlvergleich |
| RSK-003 Tagesverlust/Drawdown | DMS 04; DEC-015 | Risk/UI | UTC-Tagesgrenze und High-Water-Mark-Test |
| RSK-004 kein Auto-Compounding | DMS 04; DEC-030 | Backtest/Portfolio/Config/UI | Gewinn verändert weder 250- noch 80-USDT-Zielnotional |
| BKT-008 10×250 USDT | Nutzerauftrag | Backtest Batch | zehn isolierte Ledger-Fixtures |
| BKT-009 Einzeltest 250 USDT | Nutzerauftrag | Backtest UI/Engine | ETH-only-Test ohne andere Coins |
| BKT-010 240-USDT-Spiegellauf | DMS 04/06 | Backtest Portfolio | Parität zu Paper-Slotmodell |
| BKT-011 Baseline-/Stresskosten | DMS 06; DEC-010 | Backtest/Report | 15/40-bps-je-Seite-Fixtures |
| BKT-012 versionierte Strategieverbesserung | DMS 06; DEC-035 | Backtest/Report | Suchraum-, Mehrfenster-, Stress- und Nachbarnachweis |
| RSK-001 kein Leverage/Margin/Futures | DMS 04/11 | Config/Execution | Startblockade/Permissionscheck |
| RSK-002 Börsenfilter | DMS 04/07 | Risk/Execution | Tick/Step/Min-Notional-Tests |
| DAT-001 OHLCV persistent | Nutzerauftrag/DMS 05 | DB/Data API | Schema-/Roundtrip-Test |
| DAT-002 Startup-Vollprüfung | Nutzerauftrag | Startup/UI Health | Lücken-/Duplikat-Fixtures |
| DAT-003 inkrementelles Nachladen | Nutzerauftrag | Data Adapter | Paging-/Retry-Test |
| DAT-004 00:05-UTC-Audit | DMS 05; DEC-012 | Scheduler/UI | Scheduler-/DST-Test |
| DAT-005 Stream + REST-Fallback | Live-UI-Ziel | Data Adapter | Disconnect-/Recovery-Test |
| DAT-006 offene Kerze vorläufig | DMS 05 | Engine/UI | kein Signal auf provisional |
| DAT-007 lokale 3-Jahres-Historie | Nutzerauftrag | Chart API/UI | Range-/Datenquellentest |
| BKT-001 drei Jahre | Nutzerauftrag | Backtest/Report | Fenstergrenzen-Test |
| BKT-002 Next-bar-Fill | DMS 06 | Backtest Engine | Look-ahead-Negativtest |
| BKT-003 Kosten/Rundung | DMS 06 | Backtest/Execution | handgerechnete Fixtures |
| BKT-004 keine Bias-/synthetischen Preise | DMS 06 | Data/Backtest | Qualitäts- und Code-Review |
| BKT-005 vollständige Metriken | DMS 06 | Report/UI | Snapshot-/Formeltests |
| BKT-006 Run-Manifest | DMS 13 | Artifact Store/UI | Reproduktionslauf |
| BKT-007 Signalparität getrennt von PnL | DMS 03/06 | Test/Report | Golden-Test ohne Kapital-/Kostenabhängigkeit |
| EXE-001 getrennte Zustände | DMS 07/09 | Domain/DB/UI | State-machine-Test |
| EXE-002 Idempotency | DMS 07 | Execution | Doppel-Submit-Failure-Test |
| EXE-003 Startup-Reconciliation | DMS 07/10 | Execution/Health | Restart zwischen Submit/Antwort |
| EXE-004 Teilfill/Fehlerzustände | DMS 07 | Execution/Ledger | Adapter-Szenarien |
| EXE-005 Not-Aus | DMS 07/08 | UI/Risk | E2E und Berechtigungstest |
| EXE-006 Market-/Timeoutschutz | DMS 07; DEC-009/014/016 | Execution/Risk/UI | 25-bps-, 10-s-UNKNOWN- und 30-s-Teilfill-Test |
| UI-001 zehn Marktkarten | Nutzerauftrag/DMS 08 | Dashboard | UI-Abnahme |
| UI-002 fünf Chartzeiträume | Nutzerauftrag | Chart UI/API | Grenz-/Zeitzonentest |
| UI-003 Indikatoroverlays | Indikatorbeschreibung | Chart UI | Golden-Screenshot/Datenvergleich |
| UI-004 vorläufige Kerze sichtbar | DMS 08 | Chart UI | Visual-/Semantiktest |
| UI-005 Einheiten/Zeitzone | DMS 08 | gesamte UI | UI-Inventur |
| UI-006 Modusunterscheidung | DMS 01/08 | Header/Settings | E2E Moduswechsel |
| UI-007 Kosten am Backtest | DMS 06/08 | Report UI | Report-Abnahme |
| UI-008 feste Chartauflösungen | DMS 08; DEC-025/026 | Chart UI/API | Zeitraum-/Aggregationstest |
| OPS-001 Health | DMS 10 | Health/API/UI | Komponentenausfalltests |
| OPS-002 strukturierte Logs | DMS 10/11 | Observability | Schema-/Secret-Scan |
| OPS-003 Backup/Restore | DMS 10 | Operations | isolierter Restore-Test |
| OPS-004 Paper-Soak-Gate | DMS 10/12; DEC-018 | Operations/Release | 30 Tage, 720 Bars, 20 Trades; Maximalverlängerung 90 Tage |
| OPS-005 kein manueller Handel | DMS 11; DEC-021 | Account/Reconciliation | Fremdorder sperrt Live-Entries |
| OPS-006 lokale Pflichtalarme | DMS 10; DEC-019 | Observability/UI | persistenter P1/P2-UI-/Logtest |
| OPS-007 Backup-Retention | DMS 10; DEC-020 | Operations/Storage | 7/4/12-Retention und vierteljährlicher Restore |
| OPS-008 localhost/Windows-Service | DMS 10/11; DEC-022/023 | API/Service | Bind-/Autostart-/Restart-Test |
| SEC-001 keine Secrets | DMS 11 | alle Komponenten | Secret-Scan/Logtest |
| SEC-002 eingeschränkter Key | DMS 11 | Exchange Setup | Berechtigungsnachweis |
| SEC-003 Live-Gates | DMS 12 | Config/UI/Deploy | negativer Freischalttest |
| QLT-001 Traceability | DMS 12/15 | DMS/Testmanagement | Review ohne kritische Lücke |
| COL-001 GitHub-Repository | Nutzerauftrag/DMS 21 | Git/CI/DMS | Remote-/Secret-/Review-Check |
| COL-002 öffentliche DMS/Eigentümer-Pine, kein fremder Source | DMS 21; DEC-031/034 | Git/DMS/Release | Sichtbarkeits-, Herkunfts- und Secret-Check |

## Pflege

Neue kritische Anforderungen erhalten mindestens einen positiven und einen negativen Test. Ein `OFFEN` in der Fachquelle darf nicht durch einen grünen Implementierungstest kaschiert werden. Die Matrix enthält für DMS V1 keine kritische Fachquelle mit ausstehender Entscheidung; Test- und Implementierungsnachweise entstehen erst in den dafür vorgesehenen Phasen.
