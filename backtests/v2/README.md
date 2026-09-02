# HIXTON V2 – Forschungsstand vom 01.09.2026

Status: `RESEARCH_ONLY`. Die laufende Paperstrategie bleibt `HIXTON-SPEC-1.0`. Dieser Ordner überschreibt weder V1 noch alte Runs.

## Ausgangspunkt und Fehlerbild von V1

Der echte V1-Dreijahreslauf `68e84b25-91f9-4faa-9a65-a6699b8bd7d5` endete in der Baseline bei 3.387,67 USDT aus 2.500 USDT (+35,51 %) und im Stress bei 1.681,85 USDT (−32,73 %) mit jeweils 1.724 abgeschlossenen Trades. ETH, LINK und DOT waren in der Baseline negativ.

Die Tradeanalyse zeigt das gemeinsame Muster: Bei allen zehn Coins verloren die in weniger als 72 Stunden geschlossenen Trades in Summe Geld; die Gewinne kamen aus den länger laufenden Trends. Die Jahre 2025 und 2026 waren für V1 breit schwach. Der Schluss daraus ist ausdrücklich nicht „beliebig mehr Trades“, sondern weniger kurze Fehlausbrüche bei weiterhin ausreichender Signalzahl.

## Referenz und geprüfter Suchraum

- Vom Eigentümer bereitgestellte Pine-v6-Quelle: `strategy/pine/Der_Hixton_Indikator_v6.pine`
- SHA-256: `8af8e9a1e6c73dc66307271b7fd1141eaae02bc1fe88e8ba97b96e7a861263dd`
- 1.280 gemeinsame Parametersätze im breiten Raster: VIDYA `6/10/14/20`, Momentum `10/20/30/50`, SMA `8/24/36/60`, ATR `60/120/200/320`, Band `2,0/2,6/3,2/3,8/4,4`
- 75 Spitzensätze anschließend über drei Marktfenster und beide Kostenmodelle verglichen
- 48 direkte Nachbarn um den besten Bereich als Sensitivitätsprüfung
- Screening mit Pine-v6-Signalmathematik; Finalisten erneut mit der Produktionsengine, Decimal-Geldfluss und Binance-Mengenrundung gerechnet
- Keine Coin-Auswahl nach Ergebnis: alle zehn festgelegten Märkte bleiben in jeder Wertung

Die drei beobachteten Fenster sind keine unangetastete finale Zukunftsstichprobe. Deshalb ist das Ergebnis ein Kandidat und keine Livefreigabe.

## Ausgewählter gemeinsamer Kandidat

| Parameter | Wert |
|---|---:|
| VIDYA | 6 |
| Momentum/CMO | 20 |
| Nachglättung SMA | 8 |
| ATR | 60 |
| Bandmultiplikator | 3,80 |
| Warm-up | 400 Bars |
| Signaltimeframe | 1h |
| Semantik | Pine v6 aus der Eigentümerquelle |

Der direkte Nachbar mit Band 3,75 erzeugte im aktuellen Fenster 574 statt 549 Trades, war aber sowohl im Kosten-Stress als auch in beiden älteren Segmenten schwächer. 3,80 bleibt deshalb der Hauptkandidat; 3,75 ist nur ein dokumentierter Challenger.

## Exakter aktueller Dreijahreslauf

Fenster: `[2023-09-01 12:00 UTC, 2026-09-01 12:00 UTC)`, zehn isolierte Konten à 250 USDT.

- Primär-Run: `8dbdeb5b-a4e8-4b56-b6dc-61c7f0d54e93`
- Wiederholungs-Run: `a7c96450-29f6-437d-af97-402d9d9c58cc`
- Ausführung über den einzigen Einstieg: `py -3 src/main.py backtest all --strategy v2 --end 2026-09-01T12:00:00Z --cost both`

| Szenario | Endkapital | Rendite | Trades | kombinierter Max-Drawdown |
|---|---:|---:|---:|---:|
| Baseline, 15 bps/Seite | 6.592,22 USDT | +163,69 % | 549 | 22,00 % |
| Stress, 40 bps/Seite | 5.843,73 USDT | +133,75 % | 549 | 28,40 % |

| Coin | Baseline Ende | Baseline Rendite | Stress Rendite | Trades | Profit Factor | Max-DD |
|---|---:|---:|---:|---:|---:|---:|
| BTC | 414,47 | +65,79 % | +28,43 % | 71 | 1,26 | 34,11 % |
| ETH | 649,16 | +159,67 % | +128,46 % | 61 | 1,92 | 32,42 % |
| BNB | 388,69 | +55,48 % | +24,69 % | 60 | 1,31 | 36,05 % |
| SOL | 1.508,45 | +503,38 % | +478,72 % | 44 | 4,88 | 23,54 % |
| XRP | 557,38 | +122,95 % | +80,60 % | 55 | 1,35 | 53,15 % |
| ADA | 678,79 | +171,52 % | +142,97 % | 55 | 1,68 | 41,39 % |
| LINK | 612,46 | +144,98 % | +119,65 % | 49 | 1,48 | 37,72 % |
| AVAX | 526,69 | +110,68 % | +80,17 % | 60 | 1,47 | 35,81 % |
| DOT | 447,99 | +79,20 % | +56,70 % | 44 | 1,44 | 47,50 % |
| DOGE | 808,14 | +223,26 % | +197,11 % | 50 | 2,20 | 41,52 % |

Alle zehn Coins waren in diesem Fenster selbst im Stress positiv. Sieben von zehn überschritten 500 USDT; BTC, BNB und DOT erreichten das angestrebte Verdopplungsziel nicht. Es wird kein anderes Ergebnis behauptet.

Die Wiederholung erzeugte bytegleiche Kernartefakte:

| Artefakt | SHA-256 in beiden Runs |
|---|---|
| `metrics.json` | `1EAB7D6F9DB0D34C95CE513571CB6417FC37763F8214EFFF32EE15F31F7AAF45` |
| `trades.csv` | `E40EECBDF15674E69B77BC5F4F0D6E418BCE75ADC7CF8914BD05F9E2E34DF843` |
| `equity.csv` | `E90DD77892565E553CA8C8D04F5C07F010CD89247B2E1050DA430FEC8593FA7D` |

## Ältere Marktsegmente

Wegen echter Binance-Wartungslücken wurden keine Kerzen erfunden. Statt eines künstlich geschlossenen Dreijahresfensters wurden zwei nach Datenprüfung lückenlose Segmente verwendet.

| Segment | Szenario | Aggregierte Rendite | Trades | kombinierter Max-DD |
|---|---|---:|---:|---:|
| 16.10.2021 01:00 – 24.03.2023 13:00 UTC | Baseline | +4,26 % | 252 | 32,29 % |
| gleiches Segment | Stress | −7,82 % | 252 | 34,54 % |
| 10.04.2023 06:00 – 01.09.2024 12:00 UTC | Baseline | +77,69 % | 238 | 18,50 % |
| gleiches Segment | Stress | +64,32 % | 238 | 20,12 % |

Über alle drei Fenster waren 24 von 30 Coin-Fenstern in der Baseline und 21 von 30 im Stress positiv. Das schwächere ältere Segment enthält deutliche Einzelverluste, unter anderem bei SOL und XRP. Genau deshalb wird V2 noch nicht automatisch für Paper oder Live aktiviert.

## Abgelehnte Richtungen

- Ein Setup mit 1.837 Trades erreichte zwar +71,07 % Baseline, fiel im Stress aber auf −14,28 %. Mehr Trades allein wurden deshalb verworfen.
- Ein zusätzlicher Langfrist-Regimefilter reduzierte die Signale stark und beschädigte insbesondere XRP; er wurde nicht übernommen.
- Coin-spezifische Parameter lieferten schönere Einzelwerte, erhöhen aber Overfitting und Betriebsaufwand. V2 bleibt vorerst ein gemeinsamer Parametersatz für alle zehn Märkte.

## Nächster Freigabeschritt

1. Pine-Golden-Tests und bytegleichen V2-Reproduktionslauf dauerhaft grün halten.
2. Die vorhandene V1/V2-Auswahl der Backtest-UI gegen reale neue Runs weiter prüfen; Charts und Paper bleiben V1.
3. V2 mindestens 30 Tage nur als Shadow-/Papervergleich beobachten.
4. Erst nach Vergleich von Nettoperformance, Drawdown, Fehlerfreiheit und tatsächlicher Tradezahl entscheidet der Eigentümer über eine Paper-Umschaltung.

Das Ziel „250 USDT möglichst in drei Jahren auf 500 USDT je Coin“ bleibt eine Optimierungsrichtung, keine Zusage und kein Grund, Verlustfenster zu verstecken.
