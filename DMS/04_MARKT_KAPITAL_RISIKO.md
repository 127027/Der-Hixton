# 04 – Märkte, Kapital und Risiko

## Initiales Marktuniversum

Für DMS V1 festgelegte Binance-Spot-Paare:

1. BTC/USDT
2. ETH/USDT
3. BNB/USDT
4. SOL/USDT
5. XRP/USDT
6. ADA/USDT
7. LINK/USDT
8. AVAX/USDT
9. DOT/USDT
10. DOGE/USDT

Die Liste ist kein Versprechen, dass diese Assets in zehn Jahren die höchsten Renditen liefern. Eine solche Vorhersage ist nicht belastbar möglich. Die Auswahl priorisiert heute etablierte, liquide und unterschiedlich ausgerichtete Assets, Binance-Spot-Handelbarkeit und mindestens drei Jahre dort verfügbare Historie. Beim Abgleich am 31.08.2026 meldete die offizielle Binance-API für alle zehn Paare `TRADING` und Spot-Handel. Früheste verfügbare Binance-Tagesbars reichen von 2017 bis spätestens 2020 zurück.

Ein Paar darf nur aktiviert werden, wenn es beim jeweiligen Start weiterhin handelbar ist und die geplante Order die aktuellen Börsenfilter erfüllt. Delistings werden nicht automatisch durch ein anderes Asset ersetzt. Eine spätere Änderung der Liste erzeugt eine neue Universums-/Konfigurationsversion und neue Vergleichsbacktests.

## Kapitalmodell

### System 1 – Paper und später Live

- Gesamtstartkapital: **240,00 USDT**.
- Gemeinsamer Cashbestand für alle zehn beobachteten Paare.
- Standard: **drei Positionsslots à 80,00 USDT Zielnotional**.
- Höchstens drei gleichzeitig offene Long-Positionen.
- Startzustand: Cash, keine Position, keine Altorder.
- Ein Exit gibt den Slot und das tatsächlich zurückgeflossene Kapital wieder frei.
- Paper läuft 24/7 mit echten Binance-Marktdaten, aber simulierten Orders/Fills.

Kapital, Slotanzahl und Zielnotional müssen wegen Gebühren und verfügbarem Cash konsistent sein. Der Bot darf niemals Kredit aufnehmen oder einen negativen Cashbestand erzeugen.

### System 2 – Backtest-Labor

- Standard-Batch: zehn strikt isolierte Tests mit jeweils **250,00 USDT** Startkapital, insgesamt 2.500,00 USDT reines Simulationskapital.
- Einzeltest: frei wählbares Binance-Paar, zum Beispiel nur ETH/USDT, mit **250,00 USDT** Startkapital.
- Ziel-Quote-Budget je Einstieg ist in diesen isolierten Läufen fest 250,00 USDT oder, nach Verlusten, der kleinere verfügbare Cashbetrag; Gewinne erhöhen die nächste Zielgröße nicht automatisch.
- Jeder Test startet ohne Position und Altorder.
- Einzeltests beeinflussen einander nicht; Ergebnisse werden je Coin und zusätzlich als Vergleichstabelle gezeigt.
- Optionaler Spiegeltest bildet zusätzlich das Paper-/Live-Modell mit 240 USDT und 3×80 USDT nach.
- Es gibt kein festes Ziel „250 oder 500 USDT“. Zuerst wird korrekte Indikatorreaktion bewiesen; Performance wird ohne Wunschwert berichtet.

## Positionsgröße

Initiale Regel:

- maximal eine Long-Position pro Paar;
- kein Pyramiding;
- Zielnotional je neu belegtem Slot: 80,00 USDT;
- die 80,00 USDT sind das maximale Quote-Budget des Kaufs; bei modellierter Zahlung der Kaufgebühr im Basisasset wird die empfangene Assetmenge entsprechend reduziert;
- tatsächliches Notional höchstens verfügbarer Cash nach Reserven und Börsenfiltern;
- Menge wird abwärts auf Binance-Schrittweite gerundet;
- nach Rundung müssen Mindestmenge und Mindestnotional erfüllt sein;
- nicht investierbarer Rest verbleibt als Cash;
- keine Kreditaufnahme, kein negativer Cash-Bestand;
- eine UI-Änderung von Slotanzahl oder Positionsgröße wirkt nur auf neue Einstiege.

Automatisches Compounding ist deaktiviert. Das Zielnotional bleibt im Paper-/Live-Modell 80 USDT und im isolierten V1-Backtest 250 USDT, auch wenn Gewinne entstehen. Nach Verlusten wird höchstens der verfügbare Cashbetrag eingesetzt. Nur eine bewusst bestätigte und auditierte UI-Änderung verändert die Größe künftiger Paper-/Live-Einstiege; bestehende Positionen bleiben unberührt.

## Slotvergabe

Freie Slots gehen verbindlich an den größten auf 12 Dezimalstellen mit Round-Half-Even gerundeten Wert `(close-upper)/ATR` der jeweiligen Flip-Up-Kerze. Gleichstand wird über diese feste Reihenfolge gebrochen: BTC, ETH, BNB, SOL, XRP, ADA, LINK, AVAX, DOT, DOGE. Die Regel verwendet ausschließlich V1-Indikatorwerte und wird im Backtest mit simultanen Signalen geprüft.

Ein Kauf-Flip, der wegen voller Slots nicht ausgeführt wird, wird protokolliert. Er wird nicht später mitten im bestehenden Uptrend nachgeholt, außer die Strategie definiert ausdrücklich eine weiterhin gültige Entry-Bedingung.

## Optimierungsziel

„So viele Trades wie möglich“ darf nicht zu sinnlosen Gebührenumsätzen führen. Rangfolge:

1. korrekte Hixton-Signale und Risikoregeln;
2. maximaler Nettogewinn nach Gebühren und Slippage;
3. bei sonst vergleichbarer Nettoperformance höhere Tradezahl und Kapitalnutzung.

Timeframe oder Parameter werden nicht allein verändert, um künstlich mehr Trades zu erzeugen. Varianten müssen out-of-sample und nach Kosten bewertet werden.

## Schutzregeln, die die Strategie nicht ersetzen

Diese Regeln dürfen eine Order blockieren, erzeugen aber niemals selbst ein Handelssignal:

- Daten sind stale, lückenhaft oder noch nicht synchronisiert;
- Uhrzeit/Zeitzone unklar oder Systemuhr außerhalb Toleranz;
- Börsenmetadaten/Filter fehlen;
- API-/Authentifizierungsfehler;
- unbekannte offene Order oder Positionsabweichung;
- verfügbare Mittel reichen nicht;
- Not-Aus aktiv;
- Live-Modus nicht freigegeben;
- Preis weicht beim Absenden mehr als 25 bps vom Referenzpreis ab.

Jede Blockade wird sichtbar protokolliert.

## Verlustkontrollen

Da „alles über diesen Indikator“ laufen soll, werden keine heimlichen Stop-Loss-/Take-Profit-Signale ergänzt. Operative Schutzschalter bleiben dennoch nötig:

| Kontrolle | Verhalten | Status |
|---|---|---|
| Not-Aus | keine neuen Einstiege; Exit vorhandener Positionen nur separat bestätigen | VERBINDLICH |
| Max. Ordernotional | anfänglich 80 USDT Zielnotional und höchstens verfügbarer Cash | VERBINDLICH |
| Max. offene Positionen | anfangs drei, je Paar höchstens eine; UI-konfigurierbar | VERBINDLICH |
| Max. Tagesverlust | ab 5 % Verlust gegenüber Start-of-Day-Equity keine neuen Entries bis 00:00 UTC; Exits bleiben erlaubt | VERBINDLICH |
| Max. Drawdown live | ab 20 % unter globalem High-Water-Mark Zustand `HALTED`; keine automatische Liquidation | VERBINDLICH |
| Max. Preisabweichung vor Order | 25 bps gegenüber dem zum Intent gespeicherten Referenzpreis; bei Überschreitung blockieren | VERBINDLICH |
| Stale-data-Grenze | kein Streamupdate 90 Sekunden = `DEGRADED`; finale 1h-Bar mehr als 2 Minuten überfällig = Symbol pausieren und REST-Recovery | VERBINDLICH |

Eine Verlustschwelle soll standardmäßig neue Einstiege pausieren, nicht unkontrolliert alle Positionen als Market-Order liquidieren.

## Benchmark und Vergleich

Jede Coin- und Portfolioauswertung vergleicht die Strategie mindestens mit:

- Buy-and-Hold desselben Assets mit identischem Startkapital und Kostenannahme;
- 100 % Cash (0 % Rendite vor Inflation);
- optional einem gleichgewichteten Buy-and-Hold-Portfolio für die Aggregation.

Ein positives Ergebnis allein ist nicht ausreichend; Drawdown, Kosten, Aktivität und Benchmarkdifferenz werden gemeinsam bewertet.
