# DMS-Changelog

## 1.5.0 – 05.09.2026

- V5: alle zehn Coins mit unveränderter Pine-Referenz, aktiver V2 und 348 begrenzten Hixton-Parameter-/Filter-/Stopkombinationen geprüft; Auswahl nur im Training.
- Gemeinsame Forschungs-Regelentscheidung für Einzel-/Portfolioengine ergänzt, mit expliziter V5-Versionssperre, Schlusskurs-/Next-Open-Ausführung und unverändertem Identitätsverhalten der aktiven Strategie.
- Verlustdiagnose je Coin, Haltedauern, Kursrückgaben, Konzentration auf wenige Gewinner, realisierter/offener PnL und ältere Rückschritte dokumentiert.
- Vollständiges Kandidatenportfolio und zusätzlich nur XRP im 3×80-Konto geprüft; XRP-Nachbarsensitivität transparent als nachträgliche Diagnose gekennzeichnet. Keine Aktivierung wegen fehlender Mehrfenster-/Portfolioverbesserung.
- 86 Tests bestanden; Ruff/mypy ohne Befund. Die Hauptmesswerte wurden zweimal identisch erzeugt. Keine UI-/Pine-/Config-/Paper-Ledgeränderung.
- Ergebnisse ausschließlich unter `backtests/v5`, große Rohberichte weiter ignoriert; ein Starter und bestehende DMS-Struktur beibehalten. DEC-042 und Übergabehinweise für GPT/Codex nachgezogen.

## 1.4.0 – 05.09.2026

- Permanente Stundenverzögerung der Closed-Bar-Synchronisierung beseitigt; Watchdog repariert fehlende Stunden unabhängig vom Close-Event.
- Paper auf tatsächliches Folge-Open umgestellt, Modellzeit und Verarbeitungszeit getrennt, UTC-Zeitscheiben synchronisiert, Dust dauerhaft bewertet. Alte Paperereignisse bleiben unverändert; technischer Soak wird einmalig neu begonnen, Positionen bleiben erhalten.
- Paper-/Portfolio-Produktionsparität mit Kurslücken, Mengenrundung und Restart geprüft; nicht ausführbare Kandidaten belegen keinen Slot. UI-Portfolio verwendet aktuelle Slot-/Notionaleinstellungen und ein datenbasiertes Testende.
- Bestehende UI ohne Redesign verbessert: Freie Slots, verständlicher Wartezustand, frische offene Kerzen, korrekt gerasterte Paper-Fills und wiederverwendete Marker.
- Begrenzte coinindividuelle V4-Untersuchung und echte sukzessive Nachkaufhypothese gerechnet; keine Aktivierung wegen schwacher jüngster Periode. Positive Dreijahreswerte bleiben von kontinuierlicher Profitabilität getrennt.
- Prüfstand 74 Tests; Ruff, mypy, TypeScript und UI-Build bestanden. Live bleibt deaktiviert.
- Laptop-Abnahme 0.2.1 abgeschlossen: Startbot.bat, geprüftes SQLite-Backup, unveränderte drei Positionen/sechs Ledgerereignisse, 50 Chart-API-Prüfungen, sichtbare Chart-/Fill-/Backtestabnahme und zwei neue UI-Backtests. Details und Hashes in DMS 18.

## 1.3.1 – 02.09.2026

- Kontrollierte V1→V2-Paperaktivierung mit Sicherungshash, DOT-Migrationsschluss, V2-Start-Equity, getrenntem Session-PnL und neu gestartetem Soak dokumentiert.
- V2-Betriebsabnahme abgeschlossen: zehn valide Märkte, 50/50 Coin-/Zeitraumcharts, sichtbare Signal-/Paper-Fill-Daten, korrekte Strategie-/Ledgeranzeige und leere Browser-Fehlerkonsole.
- Dauerhaft falschen `DEGRADED`-Status nach erfolgreichem Websocket-Reconnect behoben; fremde Daten-/Auditfehler bleiben erhalten.
- Prüfstand auf 68 grüne Python-Tests angehoben; Ruff und mypy weiterhin ohne Befund. Live bleibt `LIVE_DISABLED`.

## 1.3.0 – 02.09.2026

- V2 nach ausdrücklicher Eigentümerentscheidung `DEC-037` vom Forschungskandidaten zur aktiven Paperstrategie erhoben; Live bleibt `LIVE_DISABLED`.
- Exakten V1/V2-240-USDT-Vergleich mit identischem 3×80-Risikomodell dokumentiert: V2 übertraf V1 im aktuellen Fenster normal und unter Stress.
- Persistente Paper-Strategie-Session, versionierte Positionen/Ereignisse, atomare V1→V2-Migration, Soak-Neustart und Fail-closed-Konfliktprüfung ergänzt.
- Grundprinzip `DEC-038` festgelegt: bestbelegte zulässige Verbesserung nach vollständigem Vergleich und expliziter Entscheidung übernehmen; kein automatisches Umschalten und keine Live-Freigabe durch Backtest.
- Gewünschte Mehrfachbelegung desselben Coins als V3 `ranked_repeat` getestet und wegen frühem Konzentrations-/Risikohalt verworfen; aktive V2 bleibt `one_per_symbol`.
- UI ohne Redesign um aktive Strategie, Strategie-Session, PnL seit Wechsel sowie Positionsversion/Slotzahl ergänzt.
- Konfiguration auf aktive V2 synchronisiert; Backtest-UI kennzeichnet V2 aktiv, V1 historisch und V3 verworfen.
- Prüfstand auf 67 grüne Python-Tests sowie 34 mypy-geprüfte Source-Dateien angehoben; TypeScript und Produktionsbuild bestanden, Betriebsabnahme folgt nach lokalem V2-Neustart.

## 1.2.0 – 01.–02.09.2026

- Vollständigen, vom Eigentümer übermittelten Pine-v6-Code einmalig unter `strategy/pine/` aufgenommen, gehasht und als V2-Referenz dokumentiert; V1 bleibt unverändert.
- Pine-v6-Semantik in der Strategieengine getrennt ergänzt und mit einer unabhängigen Golden-Implementierung getestet.
- V1-Verlustursache analysiert: kurze Trades unter 72 Stunden verloren über alle zehn Coins in Summe; mehr Trades allein deshalb verworfen.
- V2-Forschung sauber unter `backtests/v2` angelegt: 1.280 breite Kandidaten, 75 Mehrfenster-Finalisten und 48 Nachbarvarianten dokumentiert.
- Gemeinsamen Kandidaten 6/20/SMA8/ATR60/Band3,8 als `RESEARCH_ONLY` ausgewählt; aktuelles Fenster stark, ältere Verlustfenster ausdrücklich festgehalten, keine Paperumschaltung.
- 250→500 USDT je Coin als gewünschtes, aber nicht garantiertes Optimierungsziel präzisiert; höhere Tradezahl bleibt der Robustheit nach Kosten untergeordnet.
- Telegram auf ausdrücklichen Eigentümerwunsch aus Pflicht- und Live-Gates entfernt; lokale UI und strukturierte Logs sind die verbindlichen Überwachungskanäle.
- Kombinierte Backtest-Drawdown-Aggregation gegen abweichende Provider-Close-Millisekunden korrigiert und per Regressionstest gesichert.
- V1/V2 über denselben CLI-Einstieg und in der bestehenden Backtest-UI getrennt auswählbar gemacht; V2-Manifeste enthalten Parameter, Pine-Referenz, Semantik und `paper_approved: false`.
- Vollständigen V2-10er-Batch bytegleich wiederholt und Kernartefakt-Hashes im V2-Bericht fixiert; damaliger Prüfstand 56 grüne Python-Tests.
- Gemeinsamen 240-USDT-Spiegellauf mit drei festen 80-USDT-Slots als eigenen CLI-/UI-Modus implementiert, zweimal bytegleich reproduziert und ehrlich gegen das gleichgewichtete Buy-and-Hold-Portfolio ausgewiesen; damaliger Prüfstand 59 grüne Python-Tests.
- Vor-Live-Prüfung fand und schloss die fehlende 5-%-Tagesverlust-/20-%-Drawdown-Parität zwischen Paperledger und Portfolio-Backtest; korrigierte Risikospiegel und frühe Halts in älteren Segmenten dokumentiert.
- Backtest-UI bindet Detailtabelle nun an denselben neuesten Run wie die Karte, kennzeichnet Portfolio/Batch/Einzeltest sowie `RISIKOHALT` sichtbar und behält die abgenommene Optik bei.
- Band-4,0-Challenger trotz starkem aktuellem Fenster wegen klarer älterer Verluste verworfen; aktueller Prüfstand 61 grüne Python-Tests.
- Zentrale Arbeitsübergabe für Codex/GPT ergänzt, den 3×80-Risikospiegel verbindlich statt optional benannt und `1m = ein Monat` eindeutig von den lokal automatisch geladenen `1h`-Kerzen getrennt.

## 1.1.0 – 01.09.2026

- Dokumentationsfreeze nach ausdrücklichem Bauauftrag in die Implementierungsphase überführt.
- Genau eine `Startbot.bat` als Windows-Komfortstarter beschlossen; einziger technischer Einstieg bleibt `src/main.py`.
- README und Ordnerregel um verbindliche Sauberkeits-, Build- und Aufräumregeln ergänzt.
- Implementierter V1-Stand für Strategie, Binance-Daten, SQLite, Backtest, 24/7-Paper-Runtime und lokale TypeScript-UI dokumentiert.
- Finaler Drei-Jahres-Batch `68e84b25-91f9-4faa-9a65-a6699b8bd7d5`, bytegleicher Reproduktionslauf und ETH-Einzeltest mit echten Binance-Spot-Daten dokumentiert.
- Gate B mit 51 automatisierten Tests, zehn vollständigen Datenaudits und reproduzierbaren Ergebnis-Hashes geschlossen; positive Baseline, negativer Stressfall und hohe Drawdowns ausdrücklich festgehalten.
- Windows-Kaltstart um eine fest gepinnte IANA-Zeitzonendatenbank ergänzt; schnelle Coin-/Zeitraumwechsel gegen veraltete Chartantworten abgesichert.
- Vom Eigentümer freigegebene V1-Optik als `DEC-033` eingefroren; weitere Betriebsfunktionen müssen das bestehende Erscheinungsbild unverändert weiterverwenden.
- Paper-Checkpoints gegen Überschreiben beim Neustart gehärtet; verpasste Bar-Closes werden nachgeholt und der 30-/720-/20-Soak-Fortschritt wird persistent und ohne Layoutänderung angezeigt.
- Live-Ausführung bleibt bis zu Paper-Soak, Telegram-, Backup-/Restore-, Account- und Eigentümerfreigabe technisch gesperrt.

## 1.0.0 – 31.08.2026

- `HIXTON-SPEC-1.0` als vollständige normative V1-Strategie festgelegt: Formel, `1h`-Timeframe, Parameter, 400-Bar-Warm-up, Initialzustand, Cross-, Bar-Close- und Next-bar-Regeln.
- Sauber getrennt: implementierbare Projektspezifikation ja, unbelegte Identität mit proprietärem Hersteller-Pine nein.
- Backtestkosten verbindlich auf 15 bp je Seite in der Baseline und 40 bp je Seite im Stressfall festgelegt.
- Long-only, 3×80-USDT-Slots ohne automatisches Compounding und deterministische Slotpriorisierung in Anforderungen, Config und Traceability synchronisiert.
- Stale-Data-, Preisabweichungs-, Tagesverlust-, Drawdown-, Order-Timeout- und Teilfill-Grenzen geschlossen.
- Paper-Soak, Telegram-Alarmierung, dedizierter Bot-Account, localhost-UI, Windows-Service und Backup-/Restore-Retention festgelegt.
- Öffentliches GitHub-Repository bestätigt; fremder Pine-Source ohne Rechte ausgeschlossen, keine Open-Source-Lizenz stillschweigend angenommen.
- Entscheidungslog ohne kritische P0-/P1-Lücke geschlossen und DMS-Freigabegates von späteren Implementierungs-/Testnachweisen getrennt.
- Keine Botimplementierung und keine Backtestergebnisse erzeugt.

## 0.3.1 – 31.08.2026

- GitHub ausdrücklich als zentrale versionierte Projektablage festgeschrieben; OneDrive ist die lokale Arbeitskopie.
- Frühere Formulierung „Upload erst bei Freigabereife“ entfernt; 99 % bleibt ein separates Releasegate.
- `DEC-029` bestätigt: Slotvergabe nach stärkstem normalisiertem Hixton-Ausbruch mit festem Tie-Break.
- `DEC-030` bestätigt: 80 USDT je Slot bleiben fest bis zu einer bewussten UI-Änderung; kein automatisches Compounding.
- Verbleibende Kernblocker auf Pine-Referenz, Trading-Timeframe und Kostenmodell verdichtet.

## 0.3.0 – 31.08.2026

- `README.md` als einzige zentrale Startdatei festgelegt.
- Einziger späterer technischer Einstieg `src/main.py`; Backtest, Paper, Live und UI werden Modi statt getrennte Startprogramme.
- Reale Repository-Struktur ergänzt.
- Backtests verbindlich unter `backtests/v1`, danach `v2`, `v3`; neue Runs innerhalb einer Methodik überschreiben keine alten Ergebnisse.
- Secret-, Runtime- und Datenpfade über `.gitignore` abgesichert.

## 0.2.0 – 31.08.2026

- Binance Spot als Börse/Datenquelle festgelegt.
- Initiales Universum auf BTC, ETH, BNB, SOL, XRP, ADA, LINK, AVAX, DOT und DOGE gegen USDT festgelegt und aktuelle Binance-Handelbarkeit/Historienlänge geprüft.
- Zwei Systeme getrennt: 24/7 Paper-/Live-Vorbereitung mit 240 USDT und 3×80-USDT-Slots; Backtest-Labor mit 10×250-USDT-Batch und frei wählbarem 250-USDT-Einzeltest.
- Festes 250-/500-USDT-Performanceziel entfernt; Signalparität und ehrliche Nettoperformance getrennt.
- Maximale Nettoperformance als Primärziel, Tradezahl als Sekundärziel dokumentiert.
- GitHub-Repository, Agenten-Branches, Review-, Secret- und späteres Uploadgate dokumentiert.

## 0.1.0 – 31.08.2026

- Eingangsdatei inventarisiert und gehasht.
- Vollständige DMS-Struktur für Scope, Strategie, Märkte, Kapital, Daten, Backtest, Execution, UI, Architektur, Betrieb, Sicherheit, Tests und Konfiguration angelegt.
- Nutzeranforderungen zu zehn Coins, 250-USDT-Einzeltests, drei Jahren, Chartzeiträumen, Startup-Sync und täglichem Update abgebildet.
- Kritische fehlende Quellen und Entscheidungen zentral dokumentiert.
- Risikoregister und konkretes Betriebs-/Recovery-Runbook ergänzt.
- Keine Botimplementierung und keine erfundenen Backtestergebnisse erstellt.
