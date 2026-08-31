# 07 – Ausführung und Orders

## Grundmodell

Signal, Absicht und tatsächliche Ausführung sind getrennt:

```text
geschlossene Kerze
  -> Strategiesignal
  -> Risk-/Health-Prüfung
  -> Order-Intent
  -> Börsenorder
  -> Teil-/Vollfills
  -> Position und Cash
```

Diese Trennung ermöglicht Audit, Wiederanlauf und die Erklärung, warum ein Signal nicht zu einem Fill führte.

## Order-Intent

Pflichtfelder:

- eindeutige Intent-ID;
- Idempotency-Key aus Umgebung, Konto, Strategieversion, Symbol, Timeframe, Signalkerzenzeit und Aktion;
- Signal-ID und Signalwerte;
- gewünschte Seite, Menge/Notional und Ordertyp;
- Referenzpreis und Berechnungszeit;
- aktive Konfigurationsversion;
- Status und Blockierungsgrund.

## Verbindliche Orderarten

V1 verwendet verbindlich Market-Orders nach bestätigtem Signal. Kauforders verwenden, sofern von Binance für das Symbol erlaubt, `quoteOrderQty` mit 80 USDT Zielnotional; Verkaufsorders schließen höchstens die tatsächlich verfügbare Basisassetmenge. Vor Submit darf der aktuelle ausführbare Referenzpreis höchstens 25 bps vom Intent-Referenzpreis abweichen. Limit-/Marketable-Limit-Orders gehören nicht zu V1.

Nach Submit gelten feste Zeiten:

- nach 10 Sekunden ohne eindeutige Binance-Bestätigung: Status `UNKNOWN`, sofortige Reconciliation, keine Ersatzorder;
- Teilfills werden fortlaufend gebucht;
- bleibt eine Market-Order nach 30 Sekunden teilweise offen, wird zuerst ihr Börsenstatus geklärt und ein stornierbarer Rest storniert; keine automatische Neuorder;
- jede Überschreitung der erwarteten 25-bps-Ausführungsabweichung erzeugt mindestens einen P2-Alarm und fließt in die Paper-/Live-Auswertung ein.

## Zustände

```text
INTENT_CREATED
  -> BLOCKED
  -> SUBMITTING
      -> SUBMITTED
          -> PARTIALLY_FILLED
          -> FILLED
          -> CANCELED
          -> REJECTED
          -> UNKNOWN
```

`UNKNOWN` ist sicherheitskritisch: Es dürfen keine Ersatzorders gesendet werden, bevor der Börsenstatus über Client-ID, offene Orders, Trades und Salden abgeglichen wurde.

## Teilfills

- Jeder Fill wird separat mit Menge, Preis, Gebühr und Zeit gespeichert.
- Position basiert auf Fills, nicht auf der gewünschten Ordermenge.
- Restmenge bleibt gemäß Börsenstatus offen, wird nicht automatisch dupliziert.
- Nach 30 Sekunden gilt die oben definierte Klärungs-/Stornoregel. Ein Rest unter Binance-Mindestmenge oder Mindestnotional wird als `DUST` sichtbar verbucht und nicht durch eine regelwidrige Ersatzorder vergrößert; bei einem später regelkonformen Exit darf er mitgeschlossen werden.
- Exitmenge darf den tatsächlich verfügbaren Basisbestand nicht überschreiten.

## Restart und Reconciliation

Vor Live-Aktivierung nach jedem Start:

1. lokale offene Intents/Orders laden;
2. Börsenorder über Client-Order-ID abfragen;
3. Trades/Fills seit letztem Checkpoint laden;
4. freie/gesperrte Salden und Positionen vergleichen;
5. Differenzen als Incident markieren;
6. nur bei eindeutigem Zustand neuen Orderversand freigeben.

Lokaler Zustand ist nicht automatisch wahr; bei Live-Fills ist die Börse die Ausführungsquelle der Wahrheit. Manueller Handel auf dem Bot-Account/Subaccount ist verboten. Erkannte Fremdorders oder ungeklärte Salden führen zu `HALTED`; eine Fortsetzung erfordert geklärten Zustand und Audit, keine stille Importannahme.

## Fehlerverhalten

| Fehler | Verhalten |
|---|---|
| Rate-Limit | Retry nach Providerhinweis, Queue erhalten, keine Parallelflut |
| Netzwerk-Timeout vor Bestätigung | Status `UNKNOWN`, abfragen statt neu senden |
| Order abgelehnt | Grund speichern, keine unendliche Retry-Schleife |
| unzureichender Saldo | Intent blockieren, Alarm |
| Filteränderung | Metadaten neu laden, Menge neu bewerten, neue Intentversion erforderlich |
| stale Daten | keine neue Entry-Order |
| Stream getrennt | Signalverarbeitung pausieren, REST-Recovery |
| Prozessabsturz | atomare Persistenz und Reconciliation beim Neustart |

## Paper-/Live-Parität

Paper läuft 24/7 mit denselben Binance-Marktdaten, derselben Strategie-, Slot-, Risk- und Intentlogik wie später Live. Nur der Execution-Adapter unterscheidet sich. Startkonfiguration sind 240 USDT Modellkapital, drei Slots und 80 USDT Zielnotional. Paper-Fills bilden realistische Latenz, Binance-Gebühren und Slippage ab; ein perfekter Fill zum Signalkurs ist unzulässig.

Der Backtest ist davon getrennt: Standard sind zehn isolierte 250-USDT-Läufe oder ein einzelner gewählter 250-USDT-Lauf. Optional kann er das 240-USDT-Paperportfolio spiegeln.

## Manuelle Eingriffe

- Not-Aus: neue Entry-Intents blockieren.
- „Position schließen“ ist eine separate, paarbezogene Aktion mit Bestätigung.
- „Alle Positionen schließen“ erfordert stärkere Bestätigung und zeigt geschätzte Kosten.
- Manuelle Order außerhalb des Bots wird nicht verschwiegen; Reconciliation meldet sie.
- Änderungen an Konfiguration wirken nicht rückwirkend auf bereits eingereichte Orders.
