# 16 – Entscheidungslog und offene Punkte

Dieses Dokument ist die einzige Sammelstelle für fachliche Entscheidungen. „Default des Frameworks“ ist keine Entscheidung. Für DMS V1.3 sind alle implementierungsrelevanten P0-/P1-Entscheidungen geschlossen. Noch fehlende Zugangsdaten, Testresultate und Betriebsnachweise sind **Nachweise**, keine offenen Produktentscheidungen.

Beschlussstand: **02.09.2026, Europe/Berlin**. Änderungen nach dem DMS-Freeze benötigen eine Entscheidungs-ID, Begründung und passende Versionsanhebung.

## P0 – Strategie, Markt und Backtest

| ID | Beschluss | Status/Auswirkung |
|---|---|---|
| DEC-001 | Historischer V1-Beschluss: normative und implementierbare Referenz bleibt `HIXTON-SPEC-1.0`. Die später bereitgestellte Eigentümer-Pine-Quelle erzeugt V2 und verändert V1 nicht. | **BESCHLOSSEN**; durch DEC-034 für V2 ergänzt. |
| DEC-002 | Source `close`; VIDYA-Länge 10; Momentum/CMO 20; Nachglättung SMA 15; ATR als Wilder-RMA 200; Bandmultiplikator 2,0. Formeln und Rundungsregeln stehen normativ in DMS 03. | **BESCHLOSSEN** |
| DEC-003 | Signallogik auf Binance-Spot-Kerzen mit festem Timeframe `1h`. UI-Zeiträume sind davon unabhängig. | **BESCHLOSSEN** |
| DEC-004 | Handelsplatz und Datenquelle: Binance Spot, Quote-Asset USDT. Paper nutzt dieselben Marktdaten; Live benötigt einen eigenen Bot-Account oder Subaccount. | **BESCHLOSSEN** |
| DEC-005 | BTC, ETH, BNB, SOL, XRP, ADA, LINK, AVAX, DOT und DOGE, jeweils `/USDT`; keine automatische Ersetzung. | **BESCHLOSSEN** |
| DEC-006 | 250→500 USDT je Coin innerhalb von drei Jahren ist ein angestrebtes Optimierungsziel, kein Gewinnversprechen. Ergebnisse werden netto und vollständig berichtet; Primärziel ist robuste Nettowirkung, nicht maximale Tradezahl allein. | **BESCHLOSSEN, präzisiert 01.09.2026** |
| DEC-007 | Spot long-only; Kauf öffnet Long, Verkauf schließt Long; kein Short, Margin, Futures oder Leverage. Die aktive V2 nutzt höchstens einen Slot je Coin; abweichende Mehrfachslotmodelle benötigen eine eigene Version. | **BESCHLOSSEN; Mehrfachslot-Forschung durch DEC-039 präzisiert** |
| DEC-008 | Backtest: zehn isolierte Läufe à 250 USDT sowie Einzelmodus à 250 USDT; verpflichtender 240-USDT-Spiegellauf mit denselben Risikogates wie Paper. Paper/Live: gemeinsamer Cashpool 240 USDT, drei Slots à 80 USDT. | **BESCHLOSSEN** |
| DEC-009 | Die erste später freigegebene Liveversion verwendet Market-Orders mit den Guards aus DMS 07. | **BESCHLOSSEN** |
| DEC-010 | Kosten je Seite: Baseline 10 bp Gebühr + 2 bp Spread + 3 bp Slippage = 15 bp; Stress 10 + 10 + 20 = 40 bp. Kein BNB-/VIP-Rabatt. | **BESCHLOSSEN** |
| DEC-011 | Nur geschlossene Bars; Warm-up 400 Bars; Initialzustand nach Bar 399 `DOWN`, ohne Startorder; Cross- und Fill-Regeln exakt nach DMS 03/06. | **BESCHLOSSEN** |
| DEC-029 | Bei mehr Kaufkandidaten als freien Slots gewinnt der größte normalisierte Ausbruch `(close-upper)/ATR`; Tie-Break: BTC, ETH, BNB, SOL, XRP, ADA, LINK, AVAX, DOT, DOGE. | **BESCHLOSSEN** |
| DEC-030 | Ein Paper-/Live-Slot bleibt 80 USDT, bis der Betreiber ihn bewusst und auditierbar für künftige Entries ändert. Der isolierte Backtest nutzt fest 250 USDT Zielbudget bzw. den kleineren verfügbaren Cashbestand. Gewinne erhöhen keine der Zielgrößen automatisch. | **BESCHLOSSEN** |

## P1 – Paper-, Live- und Betriebsregeln

| ID | Beschluss | Status/Auswirkung |
|---|---|---|
| DEC-012 | Täglicher Datenaudit und Update um 00:05 UTC; UI zeigt zusätzlich Europe/Berlin. | **BESCHLOSSEN** |
| DEC-013 | 90 Sekunden ohne Streamupdate → `DEGRADED`; finale 1h-Bar mehr als 120 Sekunden verspätet → Symbol pausieren und REST-Recovery. | **BESCHLOSSEN** |
| DEC-014 | Vor Live-Submit maximal 25 bp Abweichung zwischen aktuellem Referenzpreis und geplantem Preis; darüber Intent blockieren und neu bewerten. | **BESCHLOSSEN** |
| DEC-015 | Netto-Tagesverlust von 5 % der Equity zu 00:00 UTC pausiert neue Entries bis zum nächsten UTC-Tag. 20 % Drawdown vom globalen Equity-High-Water-Mark setzt `HALTED`; keine automatische Notliquidation. | **BESCHLOSSEN** |
| DEC-016 | Ohne bestätigten Börsenstatus nach 10 Sekunden Zustand `UNKNOWN` und Reconciliation, niemals blinde Ersatzorder. Nach 30 Sekunden verbleibenden stornierbaren Teilfill-Rest stornieren; keine automatische Neuorder. | **BESCHLOSSEN** |
| DEC-017 | Offene Position am Backtestende separat mark-to-market bewerten; keinen künstlichen Exit erfinden. | **BESCHLOSSEN** |
| DEC-018 | Live-Gate: mindestens 30 Kalendertage, 720 geschlossene 1h-Bars und 20 abgeschlossene Papertrades. Sind nach 30 Tagen weniger als 20 Trades erreicht, bis 20 Trades verlängern, höchstens auf 90 Tage; danach Eigentümerentscheidung statt automatischer Live-Freigabe. | **BESCHLOSSEN** |
| DEC-019 | UI und strukturierte Logs sind die Pflichtkanäle. Der Eigentümer überwacht den Bot regelmäßig; Telegram wird ausdrücklich nicht benötigt und blockiert weder Paper noch Live. | **BESCHLOSSEN, ersetzt 01.09.2026** |
| DEC-020 | Verschlüsselte Backups außerhalb des öffentlichen Repos und außerhalb der aktiven Datenbank, bevorzugt in einem separaten OneDrive-Ziel. Retention: 7 tägliche, 4 wöchentliche, 12 monatliche Stände; Restore-Test vor Live und danach vierteljährlich. | **BESCHLOSSEN** |
| DEC-021 | Manueller Handel auf demselben Binance-Account/Subaccount ist verboten. Fremdorders oder unerklärte Salden setzen Live-Entries aus. | **BESCHLOSSEN** |
| DEC-022 | Die UI bindet ausschließlich an localhost. Netzwerkfreigabe ist eine spätere Sicherheitsentscheidung. | **BESCHLOSSEN** |
| DEC-023 | Nach bestandener Paperfreigabe Betrieb als Windows-Service mit verzögertem Autostart und Restart-on-Failure; jede Wiederaufnahme beginnt mit Startup-Reconciliation. | **BESCHLOSSEN** |
| DEC-031 | Repository `127027/Der-Hixton` ist öffentlich. DMS und eigene Projektspezifikation dürfen hinein; Secrets nie. Die vom Eigentümer ausdrücklich für das Projekt übermittelte Pine-Quelle darf eingecheckt werden; fremder Code ohne Rechte bleibt verboten. | **BESCHLOSSEN, präzisiert 01.09.2026** |
| DEC-034 | Der am 01.09.2026 übermittelte Pine-v6-Code wird einmalig unter `strategy/pine/` gespeichert und per SHA-256 fixiert. Seine Semantik ist V2-Referenz; V1 bleibt historische Wahrheit für vorhandene Runs und Paperereignisse. | **BESCHLOSSEN** |
| DEC-035 | Strategieverbesserungen werden iterativ in `backtests/v2`, `v3` usw. untersucht. Mehr Trades sind erwünscht, wenn Kosten-Stress und ältere Fenster nicht dadurch verschlechtert werden. Keine Version wird überschrieben. | **BESCHLOSSEN** |
| DEC-036 | V2-Kandidat 1 nutzt 1h, VIDYA 6, Momentum 20, SMA 8, ATR 60, Band 3,8 und 400 Warm-up-Bars. Seine unveränderliche Versionskennung bleibt `HIXTON-V2-RESEARCH-CANDIDATE-1`, auch nachdem der Status durch DEC-037 geändert wurde. | **BESCHLOSSEN; Paperstatus durch DEC-037 ersetzt** |
| DEC-037 | Der Eigentümer hat am 02.09.2026 ausdrücklich verlangt, den bislang besten Stand V2 im Paperbot zu verwenden. Der Wechsel gilt nur für Paper, erfolgt einmalig und vorwärtsgerichtet, schließt vorhandene V1-Paperpositionen kontrolliert nach Baselinekosten, bewahrt alle versionierten Ereignisse und startet den V2-Soak neu. | **BESCHLOSSEN; V2 PAPER_APPROVED, Live bleibt gesperrt** |
| DEC-038 | Grundprinzip für Verbesserungen: Der bestbelegte zulässige Kandidat wird nach dokumentiertem Vergleich und ausdrücklicher Entscheidung für Paper übernommen. Bestbelegt bedeutet nicht höchster Einzelwert, sondern Reproduzierbarkeit, Baseline/Stress, ältere Fenster, Nachbarstabilität und risikogleicher 3×80-Spiegel. Risikogrenzen werden nicht zum Schönen des Ergebnisses gelockert; Live bleibt ein eigener Entscheid. | **BESCHLOSSEN** |
| DEC-039 | Mehrere 80-USDT-Slots im selben Coin sind ein zulässiges Forschungsziel. V3 `ranked_repeat` vergab zuerst je gleichzeitigem Kandidaten einen Slot und danach Restslots an den stärksten. Der aktuelle Risikospiegel stoppte bereits am 12.10.2023 bei 287,85/282,16 USDT; V3 ist verworfen. Aktive V2 bleibt `one_per_symbol`, bis eine neue Version sie im vollständigen Prüfprogramm übertrifft. | **BESCHLOSSEN; V3 VERWORFEN** |

## P2 – Bedienung und Aufbewahrung

| ID | Beschluss | Status/Auswirkung |
|---|---|---|
| DEC-024 | Exporte: CSV und JSON; druckbarer HTML-Bericht. PDF ist optional und darf aus HTML erzeugt werden. | **BESCHLOSSEN** |
| DEC-025 | UI-Standardzeitraum: 1 Monat. | **BESCHLOSSEN** |
| DEC-026 | Chart: Heute/1W/1M nativ `1h`, 1J deterministisch `4h`, 3J deterministisch `1d`; Nutzer darf eine verfügbare Auflösung wählen. Strategie und Signale werden immer auf `1h` berechnet, nie auf aggregierten UI-Bars. | **BESCHLOSSEN** |
| DEC-027 | Markt-/Backtestdaten und Trade-/Audit-Ledger bleiben für Reproduzierbarkeit dauerhaft. Betriebslogs 90 Tage online, danach löschbar; Incidentberichte und Release-Nachweise dauerhaft. | **BESCHLOSSEN** |
| DEC-028 | Oberfläche Deutsch; technische IDs, API-Felder und Symbole bleiben unverändert/kopierbar. | **BESCHLOSSEN** |
| DEC-032 | Es gibt genau eine `Startbot.bat` für Windows. Sie enthält keine Fachlogik und delegiert an den einzigen technischen Einstieg `src/main.py start`. Weitere Starterdateien sind verboten. | **BESCHLOSSEN** |
| DEC-033 | Die am 01.09.2026 browsergeprüfte V1-Optik ist vom Eigentümer freigegeben und visuell eingefroren. Neue Betriebsinformationen verwenden die vorhandenen Karten, Tabellen, Farben, Abstände und Navigation; ein Redesign erfolgt nur nach neuer ausdrücklicher Freigabe. | **BESCHLOSSEN** |

## Vom Nutzer verbindlich vorgegeben

- Die reine Dokumentationsphase wurde nach dem DMS-Freeze beendet; anschließend wurde der Bau ausdrücklich beauftragt.
- Zehn Kryptowährungen auf Binance Spot/USDT.
- Backtest-Batch: zehn isolierte Tests à 250 USDT; Einzeltest für einen wählbaren Coin ebenfalls 250 USDT.
- 24/7-Paperbetrieb als Pflichtvorbereitung für Live.
- Paper-/Live-Start: 240 USDT als drei Positionen à 80 USDT; spätere Positionsgröße über UI änderbar.
- Dreijähriger Primärbacktest und lokale Historie.
- UI-Charts Heute, 1 Woche, 1 Monat, 1 Jahr und 3 Jahre.
- Startup-Vollprüfung aller zehn Coins und tägliches Nachziehen.
- Die Strategie basiert ausschließlich auf der dokumentierten Hixton-Logik; aktive Paperparameter sind V2, V1 bleibt historische Referenz.
- Die bestbelegte geprüfte Verbesserung soll im Paperbetrieb übernommen werden; eine Backtestwahl oder ein einzelner Spitzenwert schaltet nie automatisch um.
- Mehrere Slots im selben Coin dürfen erforscht werden, bleiben aber gesperrt, solange sie den risikogleichen Vergleich nicht gewinnen.
- GitHub ist die zentrale Projektablage; übersichtliche Struktur, ein technischer Einstiegspunkt, Backtestversionen in getrennten Versionsordnern.
- Eine einzige `Startbot.bat` startet Paper-Bot und UI; Ordnung, laufendes Aufräumen und dokumentierte Sauberkeitsregeln sind verbindlich.

## Umgang mit der Eigentümer-Pine-Quelle

Die Quelle liegt seit 01.09.2026 vor. Sie ist gehasht, versioniert und über eine unabhängige Testimplementierung gegen die Python-Engine abgesichert. Sie ersetzt weder V1-Artefakte noch bereits verbuchte Paperereignisse. Jede Parameteränderung erzeugt einen neuen Snapshot und Backtestordner; eine spätere Aktivierung gilt nur vorwärts.

## Änderungsformat nach dem Freeze

```text
Entscheidung: DEC-xxx
Datum/Zeitzone:
Entschieden von:
Beschluss:
Begründung:
Betroffene Anforderungen/Dokumente:
Neue Strategie-/Konfigurationsversion:
Erforderliche neue Tests/Backtests:
```

## Restarbeiten sind Nachweise, keine Entscheidungen

Vor Implementierung fehlen keine kritischen fachlichen Festlegungen. Vor Backtest, Paper oder Live müssen jedoch die jeweiligen Nachweise erzeugt werden: Code-/Config-/Pine-Hashes, Golden-Fixtures, echte Binance-Daten, Backtestergebnisse, API-Key-Berechtigungsprüfung, sichtbare P1/P2-Alarme, Backup-Restore und Paper-Soak. Diese Artefakte dürfen nicht vorgetäuscht werden und werden in DMS 12 über Freigabegates kontrolliert.
