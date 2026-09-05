# 18 – Backteststatus und Ergebnisnachweis

## Neueste Einzelcoin-Forschung: V5, 05.09.2026

Alle zehn Coins wurden mit 250 USDT einzeln diagnostiziert; 348 begrenzte Kombinationen aus Hixton-Parametern und expliziten Forschungsfiltern/-Stops wurden ausschließlich anhand der ersten zwei Trainingsjahre ausgewählt. Alle zehn V2-Kurztradegruppen unter 72 Stunden verlieren in Summe, während wenige lange Gewinner das Ergebnis tragen. ETH liefert einen interessanten 24-Bar-VIDYA-Steigungsfilter (jüngstes Stressjahr 213,63→278,47 USDT), aber einen älteren Rückschritt. XRP verbessert allein alle sechs Einzel-Endwerte und Drawdowns, besteht jedoch die gemeinsame Konto- und Nachbarprüfung nicht. Details für **jeden** Coin, einschließlich ADA-/DOT-Rückschritten, stehen zentral in `backtests/v5/README.md` und `backtests/v5/reports/coin-review-20260905.json`.

Das vollständige Kandidatenportfolio endet im Dreijahresfenster bei 808,30/776,04 USDT statt V2 542,49/406,29 (Baseline/Stress), aber bei einem Start im jüngsten Jahr nur bei 202,81/202,55 statt 216,71/210,47. Ein Austausch ausschließlich von XRP verschlechtert dieses Jahr ebenfalls auf 213,15/206,73. Jeder Portfoliolauf enthält einen Risikohalt. Keine neue Paperfreigabe nach DEC-042; V2 bleibt aktiv, Live bleibt gesperrt. Endwerte mit offenen Positionen werden nicht als realisierter Gewinn ausgegeben.

Hauptmesswerte in zwei Läufen identisch; Zusatzprüfung separat gekennzeichnet. 86 Tests, Ruff und mypy (37 Source-Dateien) bestanden. Kein UI-Redesign, keine Konfigurations-/Ledgeränderung und kein Neustart des Paper-Soaks für diese Forschung. Der parallel laufende Laptop meldete am 05.09.2026 um 21:47 Europe/Berlin `HEALTHY`, `PAPER`, `LIVE_DISABLED`, zehn aktuelle valide Märkte und weiterhin drei offene V2-Positionen (ADA/DOGE/ETH). Das ist ein Betriebs-, kein abgeschlossener Profitnachweis.

## Aktuelle Prüfung am 05.09.2026

Der laufende Laptop-Bot belegte bei der Prüfung alle drei Slots mit ADA, DOGE und ETH. AVAX war korrekt mit `NO_FREE_SLOT` blockiert; es existiert keine globale Ein-Positions-Sperre. V2 hatte drei eröffnete, aber noch keinen abgeschlossenen Trade. Am 05.09. um 15:11 Europe/Berlin betrug die modellierte Equity 236,85166839858 USDT, somit −0,59465736 USDT gegenüber dem V2-Start von 237,44632575858 USDT. Der frühere V1-Verlust von −2,55367424142 USDT ist separat zu behandeln. Offene Buchgewinne/-verluste schwanken und sind kein realisierter Profit.

Gefundene und korrigierte technische Defekte: permanent um eine Stunde verspätete Closed-Bar-Analyse; Paper-Fills zum Signalkerzen-Schlusskurs statt Folge-Open; fehlende separate Verarbeitungszeit; nicht erhaltene Mengenreste; ungenau gerasterte Paper-Chartmarker; keine fortlaufend angezeigte offene Chartkerze. DEC-040 beschreibt die Korrektur und den einmaligen technischen Soak-Neustart ohne Kontoreset. Historische Paperwerte werden nicht nachträglich verbessert und sind kein belastbarer Live-Latenznachweis.

Die V4-Prüfung hat die bisherigen V2-Dreijahreswerte exakt reproduziert, zusätzlich jeden Coin in einem neu gestarteten jüngsten Jahresfenster geprüft und 24 individuelle Kandidaten je Coin untersucht. Das jüngste Jahr verliert bei allen zehn V2-Einzelkonten auch unter Baselinekosten. Der neue Coin-Kandidat erhöht das Dreijahresportfolio, verschlechtert aber das jüngste Neustartjahr. Kein Wechsel. Alle Vergleichswerte und Grenzen stehen in `backtests/v4/README.md`; Quell-/Daten-/Kosten-/Filter-Nachweis unter `backtests/v4/reports/review-20260905.json`. Live bleibt deaktiviert.

### Abnahme des Laptop-Updates

Code `0e6c41d54642f1a42a7e3dce953fcfd9bc29810f`, Anwendung 0.2.1, am 05.09.2026 über die unveränderte `Startbot.bat` neu gestartet. SQLite-Backup vor dem Wechsel: `backups/hixton-before-execution-fix-20260905-151821.sqlite3`, SHA-256 `8F280DAB95078FE46F2A604677D00E79896EA2AFF4B0FAEA6974AB4EABBDDDAD`. Integrität `ok`; alle sechs alten Ledgerereignisse und alle drei Positionsdatensätze wurden gegen das Backup verglichen und sind identisch geblieben. Technische Soak-Epoche: 05.09.2026 13:19:05 UTC; kein Cash-/Positionsreset.

Nach dem Start: `HEALTHY`, `PAPER`, `LIVE_DISABLED`, zehn frische Symbolpreise und zehn Datenaudits ohne Lücken. Um 15:20 Europe/Berlin war die letzte abgeschlossene Kerze korrekt 14:00–14:59, nicht mehr eine Stunde zurück. 50/50 Chart-API-Kombinationen liefern Daten und zeitlich passende Fill-Buckets. Sichtbar geprüft: ADA-Wochenchart mit Kauf, Verkauf und Paper-Fill, BTC-Dreijahreschart, Coin-/Zeitraumwechsel und fertige Backtestergebnisse. Browserkonsole ohne Warnung/Fehler. Zwischenstand rund 239,17 USDT Equity bzw. +1,72 USDT V2-Buch-PnL; weiterhin kein abgeschlossener V2-Trade. Die Änderung dieser Bewertung ist kein nachträglicher Ledgergewinn: Marktkurse werden jetzt frisch statt aus der verspäteten Schlusskerze angezeigt.

Zwei weitere Läufe wurden direkt über die laufende UI gestartet und erfolgreich beendet. Gemeinsames Fenster: `[2023-09-05 13:00 UTC, 2026-09-05 13:00 UTC)`. Dies ist ein anderes Fenster als die fixierte V4-Forschung; Werte nicht still gegeneinander austauschen.

| Lauf | Baseline Ende | Stress Ende | Trades je Szenario |
|---|---:|---:|---:|
| 3×80, Start 240 USDT | 543,83 USDT | 406,67 USDT | 108 / 30 |
| 10×250, rechnerische Summe Start 2.500 USDT | 6.661,92 USDT | 5.910,45 USDT | 549 / 549 |

Portfolio-Run `5db104a2-974d-496d-a8f8-05293407aa6c`, `metrics.json` SHA-256 `7C66613D3BE632AE3083A4AC237F53948FC1536F7012DC4B2B82421A6C275707`. Batch-Run `81851f17-e401-46d3-bc92-9ee0a605a436`, `metrics.json` SHA-256 `00F44073D2B2CDE0DD23A0C7D23050D16C6AD50AB6D8D65A6D0090CF3B4A7827`. Beide Manifeste nennen den obigen Code-Commit. Der Portfoliohalt liegt unverändert am 06.02.2025 (Baseline) bzw. 05.02.2024 (Stress). Der frische Batch ist bei allen zehn positiv, aber BTC, BNB und DOT bleiben unter 500 USDT. Die jüngste Verlustperiode und alle Live-Blocker bleiben bestehen.

Die folgenden Abschnitte dokumentieren frühere Runs und damalige Abnahmen; sie ersetzen nicht die obige aktuelle Fehler- und Robustheitsbewertung.

## Wahrheitsgemäßer Ist-Stand

Am 01.09.2026 wurden der verbindliche V1-Drei-Jahres-Batch für alle zehn DMS-Märkte und ein ETH-Einzeltest erfolgreich ausgeführt. Die Strategie reagiert im Backtest deterministisch gemäß `HIXTON-SPEC-1.0`. Danach wurde V2 getrennt gegen die Eigentümer-Pine-Quelle entwickelt, reproduziert und am 02.09.2026 ausdrücklich für Paper freigegeben. Kein Ergebnis ist eine Zusage zukünftiger Gewinne oder eine Live-Freigabe.

Der technische Nachweis ist vollständig genug für Gate B:

- ausführbare Strategie- und Backtestengine vorhanden;
- 67 automatisierte Tests einschließlich V1-/Pine-v6-Golden-, Daten-, Paper-, Strategiemigration/-sperre, Portfolio-Risiko-, Restart-, API-, Reporting- und Charttests bestanden;
- je Markt 26.704 geschlossene 1h-Kerzen geprüft: 26.304 Auswertungsbars plus 400 Warm-up-Bars;
- zehn isolierte Konten à 250 USDT, ohne automatisches Compounding;
- Baseline- und Stresskosten auf Ein- und Ausstieg angewendet;
- frei wählbarer Einzeltest nachgewiesen;
- Wiederholung mit festem Endzeitpunkt erzeugte bytegleiche Kernartefakte.

## Verbindlicher Validierungslauf

| Feld | Nachweis |
|---|---|
| Batch-Run-ID | `68e84b25-91f9-4faa-9a65-a6699b8bd7d5` |
| Wiederholungs-Run-ID | `5192d8fd-7e16-41d8-b0de-214593878a76` |
| ETH-Einzeltest-Run-ID | `cb4d0b5e-b903-4bba-895f-c92a9da5c1d1` |
| Code-Commit | `3472415ec683597301eaed8c8ce930edec8804e8` |
| Strategie | `HIXTON-SPEC-1.0` |
| Config-SHA-256 | `b2d5caafab7f702cabcc872b7078d4bf199d45fd8e5c6dd25fcba52e428b5966` |
| Datenquelle | Binance Spot, öffentliche Marktdaten |
| Auswertungsfenster | `[2023-09-01 12:00 UTC, 2026-09-01 12:00 UTC)` |
| Warm-up-Beginn | 400 Stunden vor Auswertungsbeginn |
| Timeframe | 1h |
| Kapital | 10 × 250 USDT isoliert = 2.500 USDT rechnerische Summe |
| Ausführung | Signal auf Bar-Close, Fill zum nächsten Bar-Open |
| Baselinekosten | 10 bps Gebühr + 2 bps Spread + 3 bps Slippage = 15 bps je Seite |
| Stresskosten | 10 bps Gebühr + 10 bps Spread + 20 bps Slippage = 40 bps je Seite |
| Status | `VALID` gegen die eigene normative Spezifikation |

## Batch-Ergebnis

| Szenario | Start | Ende | Netto-PnL | Rendite | Trades | Max. Drawdown |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 2.500,00 | 3.387,67 | +887,67 | +35,51 % | 1.724 | 45,48 % |
| Stress | 2.500,00 | 1.681,85 | −818,15 | −32,73 % | 1.724 | 68,06 % |

Die Batchsumme ist nur die Summe zehn isolierter 250-USDT-Konten. Sie ist nicht mit dem 240-USDT-Paperkonto und dessen drei Slots gleichzusetzen.

## Baseline-Ergebnis je Markt

| Symbol | Endkapital | Rendite | Trades | Max. Drawdown |
|---|---:|---:|---:|---:|
| BTCUSDT | 277,06 | +10,82 % | 180 | 49,41 % |
| ETHUSDT | 178,27 | −28,69 % | 181 | 64,58 % |
| BNBUSDT | 341,12 | +36,45 % | 169 | 36,18 % |
| SOLUSDT | 551,83 | +120,73 % | 173 | 45,66 % |
| XRPUSDT | 485,23 | +94,09 % | 161 | 59,45 % |
| ADAUSDT | 375,10 | +50,04 % | 168 | 61,16 % |
| LINKUSDT | 170,69 | −31,72 % | 181 | 74,12 % |
| AVAXUSDT | 410,14 | +64,06 % | 172 | 45,16 % |
| DOTUSDT | 75,70 | −69,72 % | 169 | 86,16 % |
| DOGEUSDT | 522,51 | +109,01 % | 170 | 48,99 % |

Der ausdrücklich verlangte ETH-Einzeltest startete ebenfalls mit 250 USDT und lieferte bei identischem Fenster 181 abgeschlossene Trades. Baseline: 178,27 USDT Endkapital und −28,69 %. Stress: 73,92 USDT und −70,43 %.

## Reproduzierbarkeit

Der Wiederholungslauf verwendete denselben Code, dieselbe Konfiguration, dieselben Daten-Snapshots und denselben exklusiven Endzeitpunkt. Folgende SHA-256-Werte sind in beiden Runs identisch:

| Artefakt | SHA-256 |
|---|---|
| `metrics.json` | `9BDE37DE072ACFC37B9799013EC48AF32730D02CCF0DF63E0040907296467A01` |
| `trades.csv` | `3CF6AD814D1DD73E35D4689A38870FC91DB4BF31D4C0A8CF98046837A4375CAB` |
| `equity.csv` | `8FADBD9B8A89796D37A301708A8FDAAC7DCCA32FED1B10781FDABC85972FED73` |

`report.html` enthält absichtlich die individuelle Run-ID und wird deshalb nicht als bytegleiches Kernartefakt gewertet.

## Ergebnisformat jedes lokalen Runs

Jeder unveränderliche Run-Ordner enthält genau:

- `manifest.json`: Run-ID, Status, Zeitraum, Code-/Config-/Datenhashes und Szenarien;
- `metrics.json`: Batch- und Coinmetriken einschließlich Kosten, Benchmark und Monatsrenditen;
- `trades.csv`: Signal-/Fillzeiten, Mengen, Preise, Gebühren und Netto-PnL;
- `equity.csv`: vollständige Equity-Zeitreihe;
- `report.html`: lokal lesbarer Bericht.

Große, reproduzierbare Run-Dateien und Marktdaten werden nicht in Git eingecheckt. Der kuratierte, versionierte Nachweis liegt unter `backtests/v1/reports/`.

## Fachliche Bewertung und Grenzen

- Gate B ist technisch bestanden: Daten, Kosten, Regeln und Ergebnisse sind reproduzierbar.
- Die Baseline ist im Gesamtbatch positiv, aber drei von zehn Märkten verlieren Geld.
- Der Stressfall ist deutlich negativ; Gebühren, Spread und Slippage sind daher erfolgskritisch.
- Drawdowns bis 86,16 % je Coin und 68,06 % im Stress-Batch sind hoch. Ein positiver Endwert bedeutet keine akzeptable Live-Risikoeignung.
- Der Test optimiert keine Parameter und verspricht keine künftige Rendite.
- Eine Identität der Eigentümerquelle mit einem separat vertriebenen Herstellerprodukt wird ohne Herkunftsnachweis nicht behauptet.
- Parität der V2-Pythonsemantik zur vom Eigentümer bereitgestellten Pine-v6-Quelle wird durch einen unabhängigen Golden-Test geprüft; dies ist keine Behauptung über die Herkunft eines Herstellerprodukts.
- Der 240-USDT-Paperbetrieb ist implementiert, muss Gate C und den vorgeschriebenen Soak-Test aber noch bestehen.
- Echtes Binance-Trading bleibt technisch `LIVE_DISABLED` und ist nicht Bestandteil dieses Backtestnachweises.

## V2-Nachweis und Paperstatus

Der vollständige Stand liegt unter `backtests/v2/README.md`. Kandidat 1 verwendet 1h, VIDYA 6, Momentum 20, SMA 8, ATR 60 und Band 3,8. Im aktuellen Dreijahresfenster endeten die zehn isolierten 250-USDT-Konten zusammen bei 6.592,22 USDT (+163,69 %) in der Baseline und 5.843,73 USDT (+133,75 %) im Stress, jeweils mit 549 Trades. Alle zehn waren dort positiv; sieben überschritten 500 USDT.

Der Primär-Run `8dbdeb5b-a4e8-4b56-b6dc-61c7f0d54e93` und Wiederholungs-Run `a7c96450-29f6-437d-af97-402d9d9c58cc` wurden über denselben technischen Einstieg ausgeführt. `metrics.json`, `trades.csv` und `equity.csv` sind jeweils bytegleich. UI und CLI können V1/V2 getrennt rechnen und auflisten. Historische Manifeste behalten wahrheitsgemäß ihren damaligen Wert `paper_approved: false`; neue V2-Runs tragen seit `DEC-037` den aktuellen Freigabestatus.

## V2-Strategiereplay mit gemeinsam 3×80 USDT

Zunächst wurde die reine Strategie mit einem gemeinsamen Cashbestand von 240 USDT, höchstens drei gleichzeitig offenen Positionen, je Einstieg maximal 80 USDT und ohne automatische Hochskalierung gerechnet. Ausstiege erfolgen am nächsten 1h-Bar-Open vor neuen Einstiegen; bei Konkurrenz entscheidet die dokumentierte Ausbruchsstärke mit fester Coin-Tie-Break-Reihenfolge. Dieser erste Lauf enthielt noch nicht die Paper-Risikogates und heißt deshalb rückwirkend eindeutig `strategy-only`, nicht Paper-/Live-Spiegel.

| Szenario | Start | Ende | Netto-PnL | Rendite | Trades | Max. Drawdown | Profit Factor |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 240,00 | 528,38 | +288,38 | +120,16 % | 227 | 34,10 % | 1,37 |
| Stress | 240,00 | 436,31 | +196,31 | +81,79 % | 227 | 43,33 % | 1,22 |

Im Baselinefall wurde das Konto historisch mehr als verdoppelt; im Stressfall blieb es deutlich positiv, erreichte 480 USDT aber nicht. Die Baseline übertraf im selben Fenster ein gleichgewichtet gekauftes und gehaltenes 10-Coin-Portfolio von 490,90 USDT; im Stress lag die Strategie mit 436,31 USDT unter dessen 489,68 USDT. Von 781 erzeugten Order-Signalen wurden 456 ausgeführt; 325 Einstiegssignale wurden ausschließlich mit `NO_FREE_SLOT` dokumentiert und nicht später nachgeholt. Am Fensterende waren BTC und SOL noch offen und deshalb zum letzten Schlusskurs bewertet.

- Primär-Run: `4aa4d135-b077-4c29-a839-fa141952113b`
- Wiederholungs-Run: `060745da-5e9f-4445-a768-0b2c2da63851`
- Code-Commit beider Manifeste: `30c8db4d494d5f4a394fc869d40bbc2e62d59896`
- `metrics.json`: `62BE829B0B57354AB2EBD5F824C576ECEE86B6B9829ABA33382272C8820B0119`
- `trades.csv`: `47D6063FE662E0223D0A4FB3E6C27613D765E6C0C98A606DB6A47D707BB74AA0`
- `equity.csv`: `5B8994F48EC7B2756CC73B58839B7AF521F7D3A6E6FD2FAE34F3A5A15AE43E48`

Die drei Kernartefakte sind zwischen beiden Läufen bytegleich. Dieses Ergebnis beschreibt die Strategieauslastung mit 240 USDT, während der 10×250-Lauf ausschließlich die isolierte Eignung jedes Coins misst.

## Korrigierter Paper-/Live-Risikospiegel

Bei der Prüfung vor Live wurde eine Paritätslücke gefunden und behoben: Der gemeinsame Kapitallauf musste zusätzlich die bereits verbindlichen Paperregeln anwenden. Ab dieser Korrektur pausiert ein Verlust von 5 % gegenüber der UTC-Tagesstart-Equity neue Einstiege bis zum nächsten UTC-Tag; 20 % Drawdown vom globalen High-Water-Mark setzt dauerhaft `HALTED`. Ausstiege bleiben erlaubt, offene Positionen werden nicht notliquidiert.

| Szenario | Start | Ende | Netto-PnL | Rendite | Trades | Max. Drawdown | Risikohalt |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline | 240,00 | 542,49 | +302,49 | +126,04 % | 108 | 22,77 % | 06.02.2025 15:59:59,999 UTC |
| Stress | 240,00 | 406,29 | +166,29 | +69,29 % | 30 | 20,13 % | 05.02.2024 21:59:59,999 UTC |

Das höhere Baseline-Endkapital gegenüber `strategy-only` entstand nicht durch bessere Signale, sondern weil der Halt spätere Verlustphasen vermied. Danach wurden jedoch keine neuen Positionen mehr eröffnet. Im Baselinefall blockierte der Halt 307 weitere Einstiege, im Stressfall 487. Ein positiver Endwert darf daher nicht als drei Jahre kontinuierlicher Betrieb oder täglicher Profit gelesen werden.

- Primär-Run: `83b38ab1-cf26-4ab2-a4b1-6e1e290822ea`
- Wiederholungs-Run: `c908cf2f-5910-4dfe-97b0-e6c40465205d`
- Code-Commit beider Manifeste: `50c5327af42328824b9d06387d0bb19d7e9e92eb`
- `metrics.json`: `DBF2F599F533A2B8BED40DB71835DA2B197E3D9F306E12D22B6FA3D09BE5446C`
- `trades.csv`: `FFD91869C4FD3F4D24AA41F00B2758D2FE70B05FF9215D8B95FA14E1016B15D8`
- `equity.csv`: `3914FC1FDC11C24DCAD94F95D65EA29842678E3BDA25A9CB414338DE70DBCB6C`

Die Kernartefakte sind in beiden korrigierten Läufen bytegleich. Zwei ältere lückenlose Segmente bestätigen die fehlende Live-Reife: Im Segment 16.10.2021–24.03.2023 endete der Risikospiegel bei 227,42 USDT Baseline beziehungsweise 223,32 USDT Stress und hielt am 04.12.2021. Im Segment 10.04.2023–01.09.2024 endete er bei 207,24 beziehungsweise 201,90 USDT und hielt am 10.06.2023.

Der nachträglich mit identischem Fenster, Kapital und Risikomodell erzeugte V1-Vergleichsrun `70089491-f5b6-4388-a420-b2c7f4641225` endete bei 383,89 USDT Baseline beziehungsweise 343,47 USDT Stress. V2 lag damit im unmittelbaren Papervergleich um 158,60 beziehungsweise 62,82 USDT höher. Der Eigentümer ordnete deshalb die kontrollierte V2-Paperaktivierung an. Die älteren Verlustfenster – im Abschnitt 16.10.2021–24.03.2023 aggregiert nur +4,26 % Baseline und −7,82 % Stress – bleiben ein klarer Live-Blocker.

## V3-Mehrfachslot-Test verworfen

Run `76a78440-405a-4624-bc0b-7765558b801c` verwendete exakt die V2-Signale, erlaubte aber bis zu drei 80-USDT-Slots auf demselben stärksten gleichzeitigen Kaufsignal. Baseline endete bei 287,85 USDT (+19,94 %), Stress bei 282,16 USDT (+17,57 %); beide Fälle hielten am 12.10.2023 nach nur vier abgeschlossenen Positionen. Das ist deutlich schlechter als V2 `one_per_symbol`. V3 ist daher verworfen und nicht im Paper aktiv. Weitere Details stehen unter `backtests/v3/README.md`.

## Kontrollierte V2-Paperaktivierung und Ist-Stand

Am 02.09.2026 um 13:36:56 UTC wurde `DEC-037` einmalig ausgeführt. Vorher wurden alle zehn Märkte mit jeweils 26.704 lokalen 1h-Bars ohne Lücke auditiert und die SQLite-Datei lokal byte-/hashgleich gesichert. Die einzige offene V1-Position in DOT wurde mit dem Migrationsgrund `STRATEGY_SWITCH_TO_HIXTON-V2-RESEARCH-CANDIDATE-1` geschlossen; realisierter V1-Paper-PnL dieses Trades: `-2,55367424142 USDT`. Das historische V1-Entry- und Exit-Ereignis bleibt versioniert im Ledger.

Die neue V2-Session startete vorwärtsgerichtet bei `237,44632575858 USDT`, ohne offene Position und mit drei freien 80-USDT-Slots. Unmittelbar nach Aktivierung und Neustart lautet ihr eigener PnL `0 USDT`, ihre abgeschlossene Tradezahl `0`; historische V1-Ergebnisse werden nicht V2 zugerechnet. Der neue 30- bis 90-tägige Soak begann mit der Aktivierungszeit und ist ausdrücklich noch nicht erfüllt.

Die anschließende Betriebsabnahme bestätigte `PAPER`, `LIVE_DISABLED`, `HEALTHY`, zehn valide Märkte, Websocket-Feed, 50 von 50 verfügbare Coin-/Zeitraumcharts, sichtbare Strategie- und Paper-Fill-Markierungen sowie eine fehlerfreie Browserkonsole. Ein während der Abnahme beobachteter, bereits wieder verbundener Stream mit stehen gebliebenem Fehlerstatus wurde in Commit `3deea9e` behoben und durch einen Regressionstest abgesichert. Das ist ein Betriebsnachweis, kein Profitversprechen und keine Live-Freigabe.

Paperfreigabe bedeutet ausschließlich, dass V2 jetzt mit echten Binance-Marktdaten und simulierten Fills vorwärts geprüft wird. Sie verspricht keinen täglichen Gewinn, hebt keinen Risikohalt auf und erteilt keine Live-Freigabe.
