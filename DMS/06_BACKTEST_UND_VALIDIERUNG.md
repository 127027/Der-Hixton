# 06 – Backtest und Validierung

## Ziel

Der Backtest hat zwei getrennte Ziele: zuerst beweisen, dass der Bot auf jede historische Kerze exakt gemäß `HIXTON-SPEC-1.0` reagiert; danach reproduzierbar messen, wie diese unveränderte Strategie unter realistischen Kosten abgeschnitten hätte. Ein zusätzlicher Vergleich mit einem später rechtmäßig verfügbaren Hersteller-Indikator ist zulässig, aber keine Voraussetzung für die Projektspezifikation. Der Backtest beweist keine zukünftige Profitabilität.

## Testfenster

Primärtest je Coin:

- exakt drei vollständige Kalenderjahre im halboffenen Intervall `[report_start_utc, report_end_utc)`;
- `report_end_utc` liegt auf einer vollen UTC-Stunde und wird vor Datenabruf festgeschrieben; Standard ist der letzte planmäßig bereits finalisierte 1h-Bar-Schluss;
- `report_start_utc` ist dieselbe UTC-Uhrzeit drei Kalenderjahre früher; existiert der Tag nicht (29. Februar), wird auf den 28. Februar geklemmt;
- Datenlücken verändern niemals Start/Ende, sondern machen den Lauf bis zur Klärung ungültig;
- zusätzlich notwendiger Warm-up vor dem Start;
- Endkapital und Metriken werden nur innerhalb des Berichtsfensters gezählt;
- zusätzlich ein „volle verfügbare Historie“-Lauf, wenn die Datenqualität dies zulässt.

Für regelmäßige Neubewertung wird ein rollierendes 3-Jahres-Fenster verwendet. Ein veröffentlichter Bericht darf sein historisches Fenster nachträglich nicht ändern.

## Läufe

1. kapitalunabhängiger Golden-/Replay-Test der Indikatorwerte und Signale;
2. Standard-Batch mit zehn isolierten Einzeltests à 250 USDT;
3. Einzelmodus für ein frei gewähltes Paar, zum Beispiel nur ETH/USDT, mit 250 USDT;
4. Vergleichsaggregation der zehn isolierten Ergebnisse (2.500 USDT rechnerisches Simulationskapital, kein gemeinsamer Cashpool);
5. optionaler Paper-/Live-Spiegellauf mit gemeinsam 240 USDT und höchstens drei 80-USDT-Slots;
6. Buy-and-Hold-Benchmark je Coin;
7. Sensitivität gegenüber Kosten und Slippage;
8. Walk-forward-/Out-of-sample-Prüfung, falls Parameter überhaupt abgestimmt werden;
9. Replay-Test, der Bars chronologisch einzeln zuführt.

## Ereignisreihenfolge je Bar

Die Engine verwendet eine feste Reihenfolge:

1. zu Beginn der Bar werden Orders verarbeitet, die aus der vorherigen geschlossenen Bar stammen;
2. Fill, Gebühren, Cash und Position werden verbucht;
3. Intrabar werden ohne explizites Modell keine Entscheidungen getroffen;
4. am Bar-Ende wird die Bar finalisiert;
5. Indikator und Trendwechsel werden berechnet;
6. ein neuer Order-Intent wird frühestens für die nächste Bar vorgemerkt.

Damit kann der Schlusskurs einer Bar nicht gleichzeitig rückwirkend als Fillpreis derselben Entscheidung dienen.

## Verbindliches Kostenmodell V1

Alle Werte gelten je ausgeführter Orderseite und wirken immer zu Ungunsten der Strategie.

| Szenario | Binance-Gebühr | Spreadanteil | zusätzliche Slippage | Summe je Seite | Round-Trip |
|---|---:|---:|---:|---:|---:|
| Baseline | 10 bps | 2 bps | 3 bps | 15 bps | 30 bps |
| Stress | 10 bps | 10 bps | 20 bps | 40 bps | 80 bps |

Regeln:

- Kein BNB-Rabatt und keine VIP-Vergünstigung werden in der Baseline vorausgesetzt.
- Kauf-Fill = Next-Bar-Open × `(1 + (Spread + Slippage)/10.000)`; Verkaufs-Fill entsprechend mit Minus.
- Ein Kauf verwendet höchstens das Ziel-Quote-Budget (initial 80 bzw. 250 USDT): `gross_base = quote_spend / Kauf-Fillpreis`; Kaufgebühr wird im Basissasset abgezogen, `net_base = gross_base × (1-fee_rate)`, Cash sinkt exakt um `quote_spend`.
- Beim Verkauf wird die gesamte regelkonform handelbare Basismenge zum adversen Fillpreis bewertet; Verkaufsgebühr wird vom Quote-Erlös abgezogen, `net_quote = gross_quote × (1-fee_rate)`.
- Damit können drei 80-USDT-Kaufbudgets aus 240 USDT belegt werden, ohne einen negativen Cashbestand zu erfinden. Tatsächliche Live-Gebührenassets werden aus Börsenfills übernommen und im Papervergleich separat ausgewiesen.
- Tick Size, Step Size und Mindestnotional werden mit dem zum Lauf gespeicherten Binance-Filterstand simuliert.
- Wird später die echte kontospezifische Binance-Gebühr automatisch abgefragt, erscheint sie als zusätzliches Account-Szenario; Baseline und Stress bleiben für Vergleichbarkeit erhalten.
- Reports zeigen Brutto-PnL, Gebühr, Spread, Slippage und Netto-PnL getrennt.

## Metriken je Coin

- Start- und Endkapital;
- Netto-PnL in USDT und Nettorendite in Prozent;
- annualisierte Rendite, nur mit sauber dokumentierter Formel;
- maximaler Drawdown in USDT und Prozent samt Zeitraum;
- Anzahl abgeschlossener Trades;
- Gewinnquote;
- durchschnittlicher Gewinn/Verlust und Payoff-Ratio;
- Profit Factor;
- Gebühren und geschätzte Slippage separat;
- Exposure/Marktzeit;
- durchschnittliche und maximale Haltedauer;
- größte Gewinn-/Verlustserie;
- Sharpe und Sortino mit dokumentierter Periodisierung und risikofreiem Satz;
- Calmar;
- Buy-and-Hold-Ergebnis und Differenz;
- monatliche Renditen und Equity-Kurve.

Bei zu wenigen Trades werden instabile Kennzahlen sichtbar als „nicht aussagekräftig“ markiert.

## Batch-, Einzel- und Portfolioauswertung

- Batch: zehn Resultate mit je 250 USDT werden einzeln gezeigt und nur zum Vergleich summiert;
- Einzelmodus: Coin-Auswahl, zum Beispiel ETH, darf ohne die übrigen neun ausgeführt werden;
- Spiegelportfolio: gemeinsamer Cashpool 240 USDT, drei 80-USDT-Slots und dokumentierte Slotpriorisierung;
- keine Verwechslung zwischen rechnerischer Batchsumme und realistischem gemeinsamen Cashbestand;
- Equity nach gemeinsamer UTC-Zeitachse;
- Korrelationen der Tagesrenditen;
- Beitrag jedes Coins zu PnL und Drawdown;
- maximale gleichzeitig investierte Summe;
- separate Darstellung von Brutto-, Nettoergebnis und Tradezahl; kein festes 250-/500-USDT-Ziel.

## Validierungsdesign und Anti-Overfitting

- Parameter werden vor dem finalen Test eingefroren.
- Ein finaler Holdout wird nur einmal für die Freigabe verwendet.
- Wenn Parameter optimiert werden, werden Suchraum, Anzahl Versuche und Auswahlregel vollständig gespeichert.
- Kein Coin darf aus dem Bericht verschwinden, weil er schlecht abschneidet.
- Delistete/umbenannte Märkte und Datenverfügbarkeit werden dokumentiert.
- Sensitivität prüft Nachbarparameter; ein nur an einem exakten Punkt gutes Ergebnis gilt als fragil.
- Monte-Carlo/Trade-Reordering kann als Robustheitsanalyse dienen, ersetzt aber keine Marktzeitsimulation.
- Die Strategie wird nicht so lange verändert, bis ein gewünschter Gewinnwert erscheint.

## Mindest-Gates für fachliche Freigabe

Ein Backtest ist nur `VALID`, wenn:

- Spezifikationsparität ohne Wert-/Signalabweichung innerhalb der festgelegten numerischen Toleranz nachgewiesen ist;
- Datenqualitätsprüfung bestanden ist;
- keine fehlenden Bars im Berichtsfenster existieren oder Ausnahmen explizit dokumentiert sind;
- Kostenmodell vollständig ist;
- Konfiguration und Datenversion gehasht sind;
- alle zehn Einzeltests abgeschlossen sind;
- Lauf ohne Zufall oder mit gespeichertem Seed exakt reproduzierbar ist;
- Bericht auch Verlustperioden, nicht ausgeführte Signale und Kosten zeigt.

## Ergebnisinterpretation

Korrekte Botreaktion und Profitabilität sind zwei verschiedene Ergebnisse. Korrekte Software kann Verlust ausweisen. Dann wird die Strategie nicht still verändert; der Eigentümer entscheidet separat über eine neue Strategieversion. Hohe Tradezahl wird nur positiv bewertet, wenn die Nettoperformance nach Binance-Gebühren und Slippage nicht dadurch verschlechtert wird.
