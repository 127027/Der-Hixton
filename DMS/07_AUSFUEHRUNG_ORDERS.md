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

## Vorgeschlagene Orderarten

Für den Start ist eine Market-Order nach bestätigtem Signal der einfachste deterministische Modus (`ANNAHME`). Sie muss mit Slippage-/Abweichungsschutz versehen werden. Limit-/Marketable-Limit-Orders benötigen Regeln für Timeout, Anpassung und Nichtausführung und werden erst nach eigener Entscheidung freigegeben.

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
- Verhalten bei Timeout oder zu kleinem Rest ist noch zu definieren.
- Exitmenge darf den tatsächlich verfügbaren Basisbestand nicht überschreiten.

## Restart und Reconciliation

Vor Live-Aktivierung nach jedem Start:

1. lokale offene Intents/Orders laden;
2. Börsenorder über Client-Order-ID abfragen;
3. Trades/Fills seit letztem Checkpoint laden;
4. freie/gesperrte Salden und Positionen vergleichen;
5. Differenzen als Incident markieren;
6. nur bei eindeutigem Zustand neuen Orderversand freigeben.

Lokaler Zustand ist nicht automatisch wahr; bei Live-Fills ist die Börse die Ausführungsquelle der Wahrheit. Ungeklärte manuelle Trades auf demselben Konto führen zu `HALTED` oder einer expliziten Importentscheidung.

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
