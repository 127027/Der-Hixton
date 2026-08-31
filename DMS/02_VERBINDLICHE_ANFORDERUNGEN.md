# 02 – Verbindliche Anforderungen

Die IDs bleiben über die Entwicklung stabil. Änderungen werden nicht durch Umnummerieren versteckt.

## Strategie

| ID | Anforderung | Status |
|---|---|---|
| STR-001 | Der Bot setzt ausschließlich die freigegebene Hixton-/VIDYA-/ATR-Signallogik um. | VERBINDLICH |
| STR-002 | Signalentscheidungen verwenden nur abgeschlossene Kerzen. | VERBINDLICH |
| STR-003 | Ein Trendwechsel auf `UP` erzeugt höchstens einen Kauf-Intent; Wiederholungen im selben Trend erzeugen keinen neuen Einstieg. | ANNAHME |
| STR-004 | Ein Trendwechsel auf `DOWN` schließt eine vorhandene Long-Position; Short-Einstieg ist standardmäßig verboten. | ANNAHME |
| STR-005 | Parameter, Quelle, Timeframe, Warm-up und Initialisierung müssen aus Pine-Code/Parameter-Snapshot bestätigt werden. | OFFEN |
| STR-006 | Pine-Parität wird über Golden-Testvektoren für mindestens 1.000 aufeinanderfolgende Bars je Testmarkt belegt. | VERBINDLICH |
| STR-007 | Ein Signal wird mit Symbol, Kerzenzeit, Strategieversion, Parametern, Eingabewerten und Grund gespeichert. | VERBINDLICH |

## Märkte und Kapital

| ID | Anforderung | Status |
|---|---|---|
| MKT-001 | Genau zehn aktive USDT-Spot-Paare bilden das initiale Universum. | VERBINDLICH |
| MKT-002 | Initiales Universum: BTC, ETH, BNB, SOL, XRP, ADA, LINK, AVAX, DOT und DOGE gegen USDT. Alle zehn waren beim DMS-Abgleich auf Binance Spot im Status `TRADING` und besitzen mindestens drei Jahre Binance-Historie. | VERBINDLICH FÜR V0.1 |
| MKT-003 | Die Coinliste wird nicht automatisch nach Performance ausgetauscht. Eine spätere Überprüfung ist versioniert, vorwärtsgerichtet und benötigt neue Backtests. | VERBINDLICH |
| CAP-001 | Paper-/späteres Live-Portfolio startet mit 240,00 USDT aus einem gemeinsamen Cashbestand. | VERBINDLICH |
| CAP-002 | Paper-/Live-Anfangskonfiguration: höchstens drei gleichzeitig belegte Positionsslots mit 80,00 USDT Zielnotional je Einstieg. | VERBINDLICH |
| CAP-003 | Positionsgröße und Slotanzahl sind später in der UI änderbar; Änderungen gelten nur vorwärts, werden validiert, bestätigt und auditierbar versioniert. | VERBINDLICH |
| CAP-004 | Der Dreijahresbacktest besitzt kein festes 250-/500-USDT-Gewinnziel. Er prüft zunächst korrekte Reaktion auf den Indikator und berichtet danach die reale Nettoperformance. | VERBINDLICH |
| CAP-005 | Sind mehr gleichzeitige Kaufkandidaten vorhanden als freie Slots, entscheidet eine deterministische, noch zu bestätigende Priorisierungsregel. | OFFEN |
| CAP-006 | Primärziel der Portfolioauswahl ist maximaler Nettogewinn nach Kosten; hohe Tradezahl ist nur Sekundärziel. | VERBINDLICH |
| RSK-001 | Kein Leverage, keine Margin, keine Futures und keine API-Auszahlungsrechte. | VERBINDLICH |
| RSK-002 | Börsenfilter wie Mindestnotional, Schrittweite und Präzision werden vor jeder Order geprüft. | VERBINDLICH |

## Daten

| ID | Anforderung | Status |
|---|---|---|
| DAT-001 | OHLCV-Daten werden je Symbol und Timeframe dauerhaft gespeichert. | VERBINDLICH |
| DAT-002 | Beim Start werden Schema, Zeitraum, Lücken, Duplikate, letzte geschlossene Kerze und Datenfrische für alle zehn Paare geprüft. | VERBINDLICH |
| DAT-003 | Fehlende Daten werden inkrementell nachgeladen, paginiert und anschließend erneut validiert. | VERBINDLICH |
| DAT-004 | Täglich um 00:05 UTC läuft ein vollständiger Aktualitäts- und Lückenaudit. | ANNAHME |
| DAT-005 | Laufende Kurse kommen aus einem Stream; ein Polling-/REST-Fallback verhindert dauerhafte Blindheit. | VERBINDLICH |
| DAT-006 | Offene Kerzen werden als vorläufig markiert und nie als abgeschlossene Signalbasis behandelt. | VERBINDLICH |
| DAT-007 | UI-Historie bis drei Jahre verwendet die lokal gespeicherten, qualitätsgeprüften Daten. | VERBINDLICH |

## Backtest

| ID | Anforderung | Status |
|---|---|---|
| BKT-001 | Signalverifikation und Primärbericht nutzen exakt drei vollständige Jahre pro Paar; zusätzlich Bericht über die gesamte verfügbare qualitätsgeprüfte Historie. | VERBINDLICH |
| BKT-002 | Orders werden frühestens zum nächsten handelbaren Preis nach einem bestätigten Signal gefüllt. | VERBINDLICH |
| BKT-003 | Gebühren, Slippage, Tick-/Lot-Rundung und Mindestnotional sind Teil der Simulation. | VERBINDLICH |
| BKT-004 | Kein Look-ahead, Survivorship-Bias oder stilles Auffüllen synthetischer Preise. | VERBINDLICH |
| BKT-005 | Einzel- und Portfolioergebnisse enthalten PnL, Rendite, Drawdown, Trades, Kosten, Exposure und Benchmark. | VERBINDLICH |
| BKT-006 | Jeder Lauf erzeugt ein unveränderliches Run-Manifest und Datenqualitätsprotokoll. | VERBINDLICH |
| BKT-007 | Kapitalunabhängige Signalparität wird getrennt von PnL- und Portfoliosimulation ausgewiesen. | VERBINDLICH |
| BKT-008 | Standard-Batchlauf: zehn isolierte Coin-Backtests mit jeweils 250,00 USDT Startkapital. | VERBINDLICH |
| BKT-009 | Einzelmodus: ein frei wählbares Paar, zum Beispiel ETH/USDT, wird separat mit 250,00 USDT getestet. | VERBINDLICH |
| BKT-010 | Optionaler Paper-/Live-Spiegellauf simuliert das gemeinsame 240-USDT-Portfolio mit drei 80-USDT-Slots. | VERBINDLICH |

## Ausführung

| ID | Anforderung | Status |
|---|---|---|
| EXE-001 | Signal, Order-Intent, Börsenorder, Fill und Position sind getrennte Zustände. | VERBINDLICH |
| EXE-002 | Idempotency-Key verhindert Doppelorders je Symbol, Strategieversion und Signalkerze. | VERBINDLICH |
| EXE-003 | Beim Neustart wird zuerst mit Börsenorders, Fills und Kontostand abgeglichen; vorher keine neue Live-Order. | VERBINDLICH |
| EXE-004 | Teilfills, Ablehnung, Timeout, Rate-Limit und Netzwerkverlust besitzen dokumentierte Zustandsübergänge. | VERBINDLICH |
| EXE-005 | Not-Aus verhindert neue Einstiege. Ob vorhandene Positionen gehalten oder liquidiert werden, ist eine getrennte, bestätigungspflichtige Aktion. | VERBINDLICH |

## UI

| ID | Anforderung | Status |
|---|---|---|
| UI-001 | Dashboard zeigt zehn Märkte, Trend, Position, Datenfrische, Preis, unrealisierten PnL und letzte Aktion. | VERBINDLICH |
| UI-002 | Chartbereiche: Heute, 1W, 1M, 1J und 3J. | VERBINDLICH |
| UI-003 | Chart zeigt Kerzen, VIDYA/Trendlinie, ATR-Bänder, Kauf-/Verkaufsmarker und offene Position. | VERBINDLICH |
| UI-004 | Live-/vorläufige Kerze ist visuell eindeutig von geschlossenen Kerzen getrennt. | VERBINDLICH |
| UI-005 | Jede Zahl zeigt Einheit, Bezugszeitraum und bei Zeitwerten die Zeitzone. | VERBINDLICH |
| UI-006 | Paper und Live sind farblich/textlich deutlich; Live-Aktivierung verlangt eine explizite Bestätigung. | VERBINDLICH |
| UI-007 | Backtestseite zeigt Annahmen und Kosten direkt neben Ergebnissen. | VERBINDLICH |

## Betrieb, Sicherheit und Qualität

| ID | Anforderung | Status |
|---|---|---|
| OPS-001 | Health-Status umfasst Datenfeed, Scheduler, Datenbank, Börsenverbindung, letzte Kerze und letzte erfolgreiche Synchronisation. | VERBINDLICH |
| OPS-002 | Strukturierte Logs haben UTC-Zeit, Korrelations-ID, Schweregrad und redigieren Geheimnisse. | VERBINDLICH |
| OPS-003 | Backups und Restore werden automatisiert erstellt bzw. regelmäßig getestet. | VERBINDLICH |
| SEC-001 | Secrets stehen nie in Quellcode, DMS, Logs oder UI-Exporten. | VERBINDLICH |
| SEC-002 | API-Key erhält nur Lesen und Spot-Handel; Auszahlung ist verboten. | VERBINDLICH |
| SEC-003 | Live wird nur nach Strategieparität, Backtest, Paper-Soak-Test und Restore-Test freigeschaltet. | VERBINDLICH |
| QLT-001 | Kritische Anforderungen sind in der Traceability-Matrix mit mindestens einem Test verknüpft. | VERBINDLICH |
| COL-001 | Gemeinsames Repository ist `https://github.com/127027/Der-Hixton`; Upload erst nach Freigabe, niemals mit Secrets. | VERBINDLICH |
