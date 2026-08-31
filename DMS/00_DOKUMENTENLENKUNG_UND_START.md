# 00 – Dokumentenlenkung und Start

## Zweck

Dieses DMS ist die maßgebliche Produktspezifikation für den **Hixton-Indikator Trading Bot**. Es beschreibt, was später gebaut, getestet, angezeigt und betrieben werden soll. Es ist kein Implementierungsstand und kein Nachweis einer profitablen Strategie.

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
2. freigegebener Pine-Quellcode samt Hash und Parameter-Snapshot für die Signalformel;
3. diese DMS-Dokumente mit Status `VERBINDLICH`;
4. vorhandene Analyse `Der Hixton Indikator.md`;
5. Kommentare, Beispiele, UI-Mockups und sonstige Hinweise.

Eine spätere Implementierung darf nicht stillschweigend von einer höher priorisierten Quelle abweichen.

## Dokumentstatus

| Status | Bedeutung |
|---|---|
| VERBINDLICH | Freigegebene Soll-Vorgabe |
| ANNAHME | Arbeitsannahme, die bestätigt oder ersetzt werden muss |
| OFFEN | Entscheidung oder Quelldatei fehlt |
| NACHWEIS AUSSTEHEND | Vorgabe ist definiert, aber noch nicht durch Test/Artefakt belegt |
| VERWORFEN | Darf nicht implementiert werden |

Aktueller Paketstatus: **Spezifikationsbasis vollständig strukturiert; kritische Strategie- und Betriebsentscheidungen sind noch offen.** Deshalb ist eine ehrliche 99-%-Implementierungsfreigabe noch nicht möglich.

## Eingangsbestand vom 31.08.2026

| Datei | Umfang | SHA-256 | Bewertung |
|---|---:|---|---|
| `Der Hixton Indikator.md` | 7.226 Bytes / 27 Zeilen | `3577700EAFA4738D8941769F8275024BEDE86B6D8CB344C7B1EA8E60E7E4E117` | Analyse/Beschreibung, kein Pine-Quellcode |

Die Datei behauptet unter anderem Pine-v6-Verhalten, Bar-Close-Auswertung und fehlendes Repainting. Diese Punkte sind ohne den tatsächlichen Pine-Code **nicht verifiziert**.

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
