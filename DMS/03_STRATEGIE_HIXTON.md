# 03 – Strategie: Hixton-/VIDYA-/ATR-Logik

## Status und harte Grenze

Die vorhandene Beschreibung reicht zur Architekturplanung, aber **nicht** zur bitgenauen Strategieimplementierung. Es fehlen der Pine-Quellcode, die Input-Defaults, der Timeframe, die exakte Initialisierung und ein Referenzdatensatz. Diese Lücke darf nicht mit Internetbeispielen oder vermuteten Standardwerten geschlossen werden.

Die offizielle Hixton-Seite beschreibt grüne/rote Signalpfeile und Nutzung auf beliebigen Tickern/Timeframes, veröffentlicht dort aber keine für eine 1:1-Nachbildung ausreichende Formel. Marketingbeschreibung und Screenshots ersetzen keinen ausführbaren Referenzcode.

## Zulässige Wege zur Strategieparität

1. **Bevorzugt:** vollständiger rechtmäßig zugänglicher Pine-Code plus Einstellungen und Golden-Daten.
2. **Bei geschütztem Source:** offizielle technische Spezifikation des Rechteinhabers plus historische Exportwerte/Signale, die alle Berechnungsschritte prüfbar machen.
3. **Nur für laufendes Paper/Live, nicht für lokalen exakten Backtest:** offizielle TradingView-Alerts/Webhooks des Indikators als externe Signalquelle. Dann muss Verfügbarkeit, Duplikatschutz und Alert-Zeitpunkt getestet werden.
4. **Nicht als Hixton-Parität zulässig:** eine ähnliche öffentliche VIDYA-/ATR-Strategie nachbauen und behaupten, sie sei identisch. Das wäre eine eigene neue Strategieversion.

Wenn der Hixton-Indikator invite-only/protected ist, darf der Schutz nicht umgangen werden. Dann muss der Eigentümer bzw. Anbieter den zulässigen Integrationsweg bestätigen.

## Bekannte fachliche Bestandteile

Aus der Eingangsdatei gelten vorläufig folgende Bausteine:

1. Quelle wird durch eine adaptive VIDYA verarbeitet.
2. Adaptivität basiert auf positiven/negativen Preisänderungen und einem absoluten CMO.
3. VIDYA wird nach der Beschreibung zusätzlich über 15 Perioden geglättet.
4. ATR-Bänder liegen um VIDYA: `upper = VIDYA + ATR × bandMult`, `lower = VIDYA − ATR × bandMult`.
5. Crossover des Preises über `upper` schaltet den Trend auf `UP`.
6. Crossunder des Preises unter `lower` schaltet den Trend auf `DOWN`.
7. Zwischen den Umschaltungen bleibt der letzte Trendzustand erhalten.
8. Trendwechsel erzeugen visuelle Kauf-/Verkaufsmarker und Alerts.

Jeder Punkt bleibt `NACHWEIS AUSSTEHEND`, bis er mit dem Pine-Quellcode abgeglichen ist.

## Noch exakt zu extrahierende Pine-Details

| Feld | Warum kritisch |
|---|---|
| Pine-Version und vollständiger Source-Hash | eindeutige Referenz |
| `source` | `close`, `hl2` oder andere Quelle ändert Signale |
| `vidyaLen` | Reaktionsgeschwindigkeit |
| `momLen` | CMO-Fenster |
| VIDYA-Formel und Seed | erste Werte und Parität |
| Nachglättungslänge/-typ | Bandlage |
| `atrLen` und ATR-Variante | Bandbreite |
| `bandMult` | Signalhäufigkeit |
| verwendeter Preis beim Cross | Close, High/Low oder Source |
| Bar-Zustand | intrabar oder nur Bar-Close |
| Startwert `trendUp` | erstes gültiges Signal |
| `na`-/Warm-up-Verhalten | Beginn des handelbaren Bereichs |
| Timeframe und mögliche Multi-Timeframe-Aufrufe | Kerzenbezug/Repainting-Risiko |
| Alert-Bedingung | Trendstatus vs. echter Flip |

## Normative Zustandsmaschine

Vorbehaltlich Pine-Abgleich wird folgende sichere Zustandsmaschine verwendet:

```text
UNINITIALIZED
  -> UP,   wenn eine geschlossene Kerze die bestätigte Flip-Up-Bedingung erfüllt
  -> DOWN, wenn eine geschlossene Kerze die bestätigte Flip-Down-Bedingung erfüllt
  -> UNINITIALIZED sonst

UP
  -> DOWN nur bei bestätigtem Flip-Down
  -> UP sonst

DOWN
  -> UP nur bei bestätigtem Flip-Up
  -> DOWN sonst
```

`UNINITIALIZED` erzeugt keine Order. Falls der Pine-Code ausdrücklich mit `false`/`DOWN` startet, muss die Zustandsmaschine nach dokumentierter Entscheidung angepasst werden.

## Signal- und Positionsabbildung

Sicherer Initialvorschlag (`ANNAHME`): Spot, long-only, eine Position je Symbol, kein Pyramiding.

| Ereignis | Position vorher | Order-Intent |
|---|---|---|
| Flip-Up | flat | `ENTER_LONG` |
| Flip-Up | long | keiner; als Duplikat protokollieren |
| Flip-Down | long | `EXIT_LONG` |
| Flip-Down | flat | keiner; Zustand protokollieren |
| kein Flip | beliebig | keiner |

Ein `VERKAUFEN`-Marker bedeutet in diesem Modus **Long schließen**, nicht automatisch Short eröffnen.

## Zeit- und Fill-Regel

- Strategie wird erst ausgewertet, wenn die Kerze endgültig geschlossen ist.
- Der Signalzeitpunkt ist die Endzeit der Signalkerze in UTC.
- Ein Backtest-Fill erfolgt standardmäßig am Open der nächsten Kerze plus Kosten-/Slippage-Modell.
- Im laufenden Handel wird nach bestätigtem Bar-Close ein Order-Intent erzeugt; der reale Fill kommt von der Börse.
- Wenn nach einer Datenlücke mehrere historische Signale gefunden werden, werden alte Signale **nicht nachträglich als Live-Orders** abgesendet. Nur der aktuelle synchronisierte Zustand wird hergestellt und als Recovery-Fall gemeldet.

## Kein Repainting – Abnahmedefinition

„Kein Repainting“ gilt nur als nachgewiesen, wenn:

- keine zukünftigen Bars in die Berechnung einfließen;
- mögliche `request.security`-Aufrufe korrekt ohne Look-ahead arbeiten;
- Signale nach Bar-Close unverändert bleiben;
- ein Replay-/Streaming-Test dieselben bestätigten Signale liefert wie der Batchlauf;
- mindestens drei verschiedene Marktphasen geprüft wurden.

## Pine-Paritätsnachweis

Vor Strategie-Freigabe werden aus TradingView/Pine exportiert:

- Zeitstempel, OHLCV;
- VIDYA, obere/untere Bänder;
- Trendzustand;
- Flip-Up/Flip-Down;
- aktive Parameter.

Die spätere Engine muss nach Rundungsdefinition dieselben Zustände und Signale erzeugen. Preislinien dürfen eine dokumentierte numerische Toleranz haben; Signalabweichungen müssen **0** sein.

## Verbotene stillschweigende Erweiterungen

- RSI-, ADX-, Volumen-, Nachrichten- oder Trendfilter;
- Take-Profit, Stop-Loss oder Trailing Stop;
- Zeitfilter, Cooldown oder Mindesthaltedauer;
- Wechsel des Timeframes je Marktlage;
- optimierte Parameter je Coin;
- Nachkaufen oder Pyramiding;
- Short-Handel.

Solche Erweiterungen benötigen eine neue Strategieversion, eigene Backtests und eine explizite Entscheidung.
