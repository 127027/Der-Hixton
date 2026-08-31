# 06 – Backtest und Validierung

## Ziel

Der Backtest hat zwei getrennte Ziele: zuerst beweisen, dass der Bot auf jede historische Kerze genauso wie der freigegebene Hixton-Indikator reagiert; danach reproduzierbar messen, wie diese unveränderte Strategie unter realistischen Kosten abgeschnitten hätte. Er beweist keine zukünftige Profitabilität.

## Testfenster

Primärtest je Coin:

- exakt drei vollständige Jahre;
- Start und Ende werden vor dem Lauf als UTC-Zeitpunkte festgeschrieben;
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

## Kostenmodell

Jeder Lauf dokumentiert:

- Maker-/Taker-Gebühr in Basispunkten;
- angenommener Ordertyp;
- Slippage in Basispunkten oder ein klar beschriebenes dynamisches Modell;
- Spread, sofern nicht schon in Slippage enthalten;
- Rundung nach Tick/Step Size;
- Mindestnotional und abgelehnte Kleinstorders;
- mögliche Gebührenzahlung in anderer Währung und deren Umrechnung.

Bis Börse und Gebührenstufe feststehen, werden Ergebnisse nicht als final bezeichnet. Mindestens drei Szenarien:

- günstig;
- realistisch/baseline;
- Stress mit deutlich höheren Kosten/Slippage.

Konkrete Basispunkte sind `OFFEN` und dürfen nicht erfunden werden.

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

- Pine-Parität ohne Signalabweichung nachgewiesen ist;
- Datenqualitätsprüfung bestanden ist;
- keine fehlenden Bars im Berichtsfenster existieren oder Ausnahmen explizit dokumentiert sind;
- Kostenmodell vollständig ist;
- Konfiguration und Datenversion gehasht sind;
- alle zehn Einzeltests abgeschlossen sind;
- Lauf ohne Zufall oder mit gespeichertem Seed exakt reproduzierbar ist;
- Bericht auch Verlustperioden, nicht ausgeführte Signale und Kosten zeigt.

## Ergebnisinterpretation

Korrekte Botreaktion und Profitabilität sind zwei verschiedene Ergebnisse. Korrekte Software kann Verlust ausweisen. Dann wird die Strategie nicht still verändert; der Eigentümer entscheidet separat über eine neue Strategieversion. Hohe Tradezahl wird nur positiv bewertet, wenn die Nettoperformance nach Binance-Gebühren und Slippage nicht dadurch verschlechtert wird.
