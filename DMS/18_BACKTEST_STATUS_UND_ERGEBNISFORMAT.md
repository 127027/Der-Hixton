# 18 – Backteststatus und Ergebnisformat

## Wahrheitsgemäßer Ist-Stand

Stand 31.08.2026 wurde **kein valider Backtest ausgeführt**. Strategie, Parameter, `1h`-Timeframe und Kostenmodell sind dokumentiert; für einen echten Lauf fehlen weiterhin:

- ausführbarer Bot-Strategie-/Backtestcode;
- Golden-Testartefakte aus `HIXTON-SPEC-1.0`;
- vollständiger Binance-Datensnapshot für die festgelegte Coinliste;
- historische Datensnapshots;
- Backtestengine und Ergebnisartefakte.

Jede konkrete Rendite-, Trefferquote- oder Drawdownzahl wäre derzeit erfunden. Die vorhandene Datei bewertet nur den beschriebenen Indikator; sie enthält keinen reproduzierbaren Performancebeleg.

## Verbindlicher Testumfang

- kapitalunabhängiger Signal-/Spezifikationsparitätstest;
- Standard-Batch: zehn isolierte Einzeltests × 250 USDT;
- Einzelmodus: ein gewählter Coin, zum Beispiel ETH, mit 250 USDT;
- primär drei vollständige Jahre plus Warm-up;
- rechnerischer Vergleich der zehn isolierten Resultate mit 2.500 USDT Gesamtsimulationskapital;
- optionaler Paper-/Live-Spiegellauf mit 240 USDT und drei 80-USDT-Slots;
- volle verfügbare Historie als Zusatz;
- Baseline- und Stresskosten;
- Buy-and-Hold-Benchmark;
- reproduzierbares Manifest und Datenqualitätsbericht.

## Ergebnistabelle je Coin

| Feld | Wert |
|---|---|
| Symbol | aus bestätigter Liste |
| Zeitraum | Start UTC bis Ende UTC |
| Timeframe | 1h |
| Startkapital | 250,00 USDT |
| Endkapital | zu berechnen |
| Nettogewinn | zu berechnen |
| Nettorendite | zu berechnen |
| Signalparität | bestanden / nicht bestanden / nicht geprüft |
| Max. Drawdown | zu berechnen |
| Trades | zu berechnen |
| Gewinnquote | zu berechnen |
| Profit Factor | zu berechnen |
| Gebühren | zu berechnen |
| Slippage | zu berechnen |
| Exposure | zu berechnen |
| Buy-and-Hold | zu berechnen |
| Qualitätsstatus | valid / invalid / stale |

## Batch- und Portfolioübersicht

| Feld | Definition |
|---|---|
| Batch-Startkapital | 2.500,00 USDT rechnerisch, 10×250 isoliert |
| Batch-Endkapital | Summe der zehn isolierten Test-Equities |
| Spiegelportfolio-Start | 240,00 USDT gemeinsamer Cashpool, 3×80 Slots |
| Spiegelportfolio-Ende | gemeinsame Cash-/Positions-Equity |
| Netto-PnL | Endkapital minus Startkapital |
| Portfolio-Drawdown | aus synchronisierter Gesamt-Equity |
| Tradezahl/Kapitalnutzung | je Coin, Batch und Spiegelportfolio getrennt |
| bester/schlechtester Beitrag | sichtbar, ohne Auswahlbias |
| Gesamtkosten | Gebühren + modellierte Slippage |

## Trade-Liste

Jeder Trade enthält:

- Symbol;
- Entry-/Exit-Signal-ID und Barzeiten;
- Intent-/Order-/Fill-Referenzen;
- Mengen und Preise;
- Brutto-/Netto-PnL;
- Gebühren/Slippage;
- Haltedauer;
- Strategie-/Konfigurations-/Datenversion;
- Exitgrund;
- Kennzeichen, falls am Testende nur mark-to-market bewertet.

## Report-Warnungen

Prominent anzeigen bei:

- weniger als drei vollständigen Jahren;
- Datenlücke/Revision;
- unbekannten oder vom V1-Baseline-/Stressmodell abweichenden Gebühren;
- fehlender Spezifikationsparität;
- weniger Trades als für stabile Metriken nötig;
- Ergebnis aus In-sample-Optimierung;
- veralteter Strategie-/Datenversion;
- offenem Trade am Testende;
- nicht angewendeter Slotpriorisierung im 240-USDT-Spiegellauf.
