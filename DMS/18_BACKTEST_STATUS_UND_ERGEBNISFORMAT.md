# 18 – Backteststatus und Ergebnisnachweis

## Wahrheitsgemäßer Ist-Stand

Am 01.09.2026 wurden der verbindliche Drei-Jahres-Batch für alle zehn DMS-Märkte und ein ETH-Einzeltest erfolgreich ausgeführt. Die Strategie reagiert im Backtest deterministisch gemäß `HIXTON-SPEC-1.0`. Die Ergebnisse sind kein Beleg für Herstellerparität und keine Zusage zukünftiger Gewinne.

Der technische Nachweis ist vollständig genug für Gate B:

- ausführbare Strategie- und Backtestengine vorhanden;
- 47 automatisierte Tests einschließlich Golden-, Daten-, Paper-, API- und Charttests bestanden;
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
- Herstellerparität bleibt unbelegt, solange kein rechtmäßig verfügbarer Pine-Referenzcode verglichen wurde.
- Der 240-USDT-Paperbetrieb ist implementiert, muss Gate C und den vorgeschriebenen Soak-Test aber noch bestehen.
- Echtes Binance-Trading bleibt technisch `LIVE_DISABLED` und ist nicht Bestandteil dieses Backtestnachweises.
