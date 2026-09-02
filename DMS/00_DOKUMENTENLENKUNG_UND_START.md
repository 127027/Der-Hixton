# 00 – Dokumentenlenkung und Start

## Zweck

Dieses DMS ist die maßgebliche Produktspezifikation für den **Hixton-Indikator Trading Bot**. Es beschreibt, was gebaut, getestet, angezeigt und betrieben wird. Der aktuelle Implementierungs- und Nachweisstand steht ergänzend in Dokument 14 und 18; auch ein valider historischer Test ist kein Nachweis zukünftiger Profitabilität.

## Geltungsbereich

Die Dokumentation deckt ab:

- die exakt abzugleichende Hixton-/VIDYA-/ATR-Signallogik;
- zehn Kryptowährungspaare auf Binance Spot;
- Einzel- und Portfoliobacktests mit klaren Annahmen;
- Marktdatenbeschaffung, Lückenprüfung und tägliche Aktualisierung;
- Order-, Kapital- und Sicherheitsregeln;
- Live-UI mit Chartzeiträumen Heute, 1 Woche, 1 Monat, 1 Jahr und 3 Jahre;
- Architektur, Datenmodell, Betrieb, Wiederanlauf, Monitoring und Recovery;
- Tests, Abnahme, Nachvollziehbarkeit und einen schrittweisen Build-Plan.

## Rangfolge der Quellen

Bei einem Widerspruch gilt diese Reihenfolge:

1. schriftlich vom Eigentümer freigegebene Entscheidung im Entscheidungslog;
2. für den aktiven Paperbetrieb die in `DEC-037` freigegebene V2 samt unveränderlichem Snapshot in Dokument 03 und `backtests/v2/candidate.json`;
3. diese DMS-Dokumente mit Status `VERBINDLICH`;
4. die am 01.09.2026 vom Eigentümer bereitgestellte Pine-v6-Quelle samt Hash; sie überschreibt historische V1-Nachweise nicht;
5. vorhandene Analyse `Der Hixton Indikator.md`;
6. Kommentare, Beispiele, UI-Mockups und sonstige Hinweise.

Eine spätere Implementierung darf nicht stillschweigend von einer höher priorisierten Quelle abweichen.

## Dokumentstatus

| Status | Bedeutung |
|---|---|
| VERBINDLICH | Freigegebene Soll-Vorgabe |
| ANNAHME | Arbeitsannahme, die bestätigt oder ersetzt werden muss |
| OFFEN | Entscheidung oder Quelldatei fehlt |
| NACHWEIS AUSSTEHEND | Vorgabe ist definiert, aber noch nicht durch Test/Artefakt belegt |
| VERWORFEN | Darf nicht implementiert werden |

Aktueller Paketstatus: **DMS V1.3 ist fachlich entscheidungsvollständig; V2 ist die aktive Paperstrategie, V1 bleibt Historie und V3 ist ein verworfener Mehrfachslot-Versuch.** Kritische Produktentscheidungen stehen nicht auf `OFFEN`. Golden-/Unit-/API-Tests, echte Binance-Daten, reproduzierbare Backtests und Browser-Abnahme liegen vor. Der neu gestartete 30- bis 90-tägige V2-Paper-Soak, externes Backup/Restore, dedizierter Live-Account und Live-Freigabe bleiben `NACHWEIS AUSSTEHEND`; `LIVE_DISABLED` bleibt technisch erzwungen. Telegram ist auf ausdrücklichen Eigentümerwunsch kein Pflichtkanal.

## Arbeitsübergabe vom 02.09.2026

- Der Eigentümer hat V2 ausdrücklich für Paper freigegeben. Aktiver Laufzeitstand ist **V2 `HIXTON-V2-RESEARCH-CANDIDATE-1`**; die unveränderliche Kennung wird trotz neuem Status nicht umbenannt. V1-Ledger und V1-Runs bleiben erhalten. Live ist nicht freigegeben.
- Der V2-10×250-Test war im aktuellen Dreijahresfenster stark. Der echte 3×80-Paper-/Live-Risikospiegel hielt jedoch im aktuellen Fenster und in beiden älteren Prüfsegmenten wegen der verbindlichen Risikogrenzen vorzeitig an. Er belegt deshalb keinen kontinuierlichen Dreijahresbetrieb und keine tägliche Gewinnerwartung.
- Band 4,0 wurde trotz besserem aktuellen Fenster wegen schwacher älterer Segmente verworfen. Der nächste Bearbeiter darf diesen Challenger nicht ohne neue robuste Nachweise reaktivieren und die 5-%-Tagesverlustpause oder den 20-%-Drawdown-Halt nicht zur Ergebnisverbesserung lockern.
- Der erste V3-Versuch erlaubte die vom Eigentümer gewünschte Mehrfachbelegung eines Coins: zuerst je gleichzeitigem Kandidaten ein Slot, danach alle freien Slots an den stärksten Kandidaten. Er endete schon am 12.10.2023 im Risikohalt bei 287,85 USDT Baseline bzw. 282,16 USDT Stress und ist verworfen. Aktive V2 bleibt bei höchstens einem Slot je Coin.
- Grundprinzip: Die bestbelegte zulässige Version wird nach explizitem, protokolliertem Wechsel für Paper übernommen. Ein einzelner Spitzenwert genügt nicht; Kosten-Stress, Altfenster, Risikospiegel und Reproduzierbarkeit bleiben Pflicht. Live benötigt immer eine eigene Freigabe.
- Prüfstand vor dem Betriebswechsel: 67 grüne Python-Tests, Ruff, mypy, TypeScript und Produktionsbuild bestanden; die Browserprüfung wird nach dem lokalen V2-Neustart erneut ausgeführt. Alle früher geprüften 50 Kombinationen aus zehn Coins und fünf Chartzeiträumen lieferten Daten.
- Marktdaten sind lokale, automatisch nachgeladene `1h`-Kerzen. UI-Kürzel `1m` bedeutet einen Monat. Datenbank, Marktdaten, Logs und große reproduzierbare Run-Artefakte bleiben durch `.gitignore` lokal.
- Gemeinsamer Übergabestand liegt im Branch `codex/build-foundation-v1` und Pull Request 2. Dokument 18 und `backtests/v2/README.md` enthalten die belastbaren Run-IDs, Hashes, Ergebnisse und Grenzen.

## Eingangsbestand vom 31.08.2026

| Datei | Umfang | SHA-256 | Bewertung |
|---|---:|---|---|
| `Der Hixton Indikator.md` | 7.226 Bytes / 27 Zeilen | `3577700EAFA4738D8941769F8275024BEDE86B6D8CB344C7B1EA8E60E7E4E117` | Analyse/Beschreibung, kein Pine-Quellcode |
| `Der_Hixton_Indikator_v6.pine` | Eigentümerquelle vom 01.09.2026 | `8AF8E9A1E6C73DC66307271B7FD1141EAAE02BC1FE88E8BA97B96E7A861263DD` | verbindliche Formelreferenz der aktiven Paper-V2, nicht rückwirkend für V1 |

Die ursprüngliche Markdown-Analyse bleibt als unverändertes Eingangsmaterial erhalten. Der später vom Eigentümer vollständig übermittelte Pine-v6-Code liegt einmalig unter `strategy/pine/` und ist die Referenz für V2. Die selbstständige V1-Projektdefinition in Dokument 03 und sämtliche V1-Runs bleiben unverändert erhalten.

## Dokumentenkarte

| Datei | Inhalt |
|---|---|
| `01_PRODUKTVISION_SCOPE.md` | Ziel, Grenzen und Nutzerrollen |
| `02_VERBINDLICHE_ANFORDERUNGEN.md` | funktionale und nichtfunktionale Anforderungen |
| `03_STRATEGIE_HIXTON.md` | normative Signal- und Zustandslogik |
| `04_MARKT_KAPITAL_RISIKO.md` | zehn Märkte, 3×80-USDT-Modell und Schutzregeln |
| `05_MARKTDATEN_UND_AKTUALISIERUNG.md` | Download, Lücken, Startup und Mitternachtsjob |
| `06_BACKTEST_UND_VALIDIERUNG.md` | 3-Jahres-Test, Kosten, Metriken und Anti-Overfitting |
| `07_AUSFUEHRUNG_ORDERS.md` | Signal-zu-Order-Lebenszyklus |
| `08_UI_UX_SPEZIFIKATION.md` | Screens, Charts, Status und Bedienregeln |
| `09_SYSTEMARCHITEKTUR_DATENMODELL.md` | Komponenten, Zustände und persistente Daten |
| `10_BETRIEB_MONITORING_RECOVERY.md` | Start, Scheduler, Logs, Backup und Störungen |
| `11_SICHERHEIT_COMPLIANCE.md` | Schlüssel, Rechte, Audit und Haftungshinweise |
| `12_TESTS_ABNAHMEKRITERIEN.md` | Testpyramide und Freigabegates |
| `13_KONFIGURATION_UND_SCHEMATA.md` | Konfigurationsfelder und Validierung |
| `14_BUILD_PLAN_UND_DEFINITION_OF_DONE.md` | spätere Umsetzungsreihenfolge |
| `15_TRACEABILITY_MATRIX.md` | Anforderung → Test → UI/Artefakt |
| `16_ENTSCHEIDUNGSLOG_UND_OFFENE_PUNKTE.md` | zentrale Unklarheiten und Beschlüsse |
| `17_GLOSSAR.md` | eindeutige Begriffe |
| `18_BACKTEST_STATUS_UND_ERGEBNISFORMAT.md` | wahrheitsgemäßer Ist-Stand und Ergebnisformat |
| `19_RISIKOREGISTER.md` | fachliche, technische und betriebliche Restrisiken |
| `20_BETRIEBSRUNBOOK.md` | konkrete Bedien- und Störungsabläufe |
| `21_GITHUB_ZUSAMMENARBEIT.md` | Repository, Branches, Reviews und späterer Upload |
| `22_QUELLEN_UND_BINANCE_PRUEFUNG.md` | offizielle Schnittstellen und geprüfter Marktstatus |
| `23_ORDNERSTRUKTUR_UND_EINSTIEGSPUNKT.md` | ein Projektstart, ein technischer Einstieg und Backtestversionen |

## Änderungsprozess

1. Jede fachliche Änderung erhält eine Entscheidungs-ID (`DEC-xxx`).
2. Betroffene Anforderungen und Tests werden aktualisiert.
3. Änderungen an der Strategie erhöhen die Strategieversion und machen bestehende Backtestergebnisse ungültig.
4. Eine Backtestausgabe nennt immer Git-/Build-Version, Strategiehash, Konfigurationshash, Datenhash und Kostenmodell.
5. Nur als `VERBINDLICH` markierte Entscheidungen dürfen gebaut werden.

## Nichtverhandelbare Wahrheitsregeln

- Keine erfundenen Backtestwerte.
- Keine Ergebnisgarantie oder Renditezusage.
- Kein Look-ahead, kein Repainting, keine Verwendung einer noch offenen Kerze zur Orderentscheidung.
- Keine heimliche Optimierung auf die Zielrendite.
- Keine Änderung der Strategie durch UI, Datenbereinigung oder Risikocode ohne dokumentierte Entscheidung.
- Ein blockierter Trade muss mit Ursache protokolliert werden; er darf nicht still verschwinden.
