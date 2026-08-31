# 08 – UI-/UX-Spezifikation

## UI-Grundsätze

- Die UI zeigt Fakten und Status, keine Renditeversprechen.
- `BACKTEST`, `PAPER`, `LIVE_DISABLED` und `LIVE` sind permanent sichtbar.
- Datenzeit, letzte abgeschlossene Kerze und Live-/vorläufiger Status sind sichtbar.
- Kritische Aktionen benötigen Bestätigung; Lesen und Navigieren nicht.
- Rot/Grün wird zusätzlich durch Text/Icon ergänzt, damit Farbe nie allein Bedeutung trägt.
- Deutsche Oberfläche; technische IDs dürfen kopierbar sein.

## Hauptnavigation

1. Übersicht
2. Chart & Signale
3. Positionen & Orders
4. Backtests
5. Datenqualität
6. System & Logs
7. Einstellungen
8. Dokumentation/Versionen

## Übersicht

Kopfbereich:

- Botname und Version;
- Modus;
- Gesamtstatus `HEALTHY/DEGRADED/HALTED`;
- Börsen-/Datenverbindung;
- letzte Synchronisation;
- aktuelle UI-Zeitzone;
- Not-Aus.

Zehn Marktkarten zeigen:

- Symbol;
- aktuellen/letzten Preis mit Zeit;
- Trend `UP/DOWN/UNINITIALIZED`;
- letztes Signal und Signalkerzenzeit;
- Position `FLAT/LONG/UNKNOWN`;
- Positionsmenge, Einstieg, Marktwert;
- unrealisierten PnL;
- isoliertes Cash und Equity;
- Datenfrische und Lückenstatus;
- offene/ungeklärte Order.

## Chart & Signale

Pflichtsteuerungen:

- Coin-Auswahl;
- Zeitraum: **Heute**, **1 Woche**, **1 Monat**, **1 Jahr**, **3 Jahre**;
- sichtbarer Daten-/Trading-Timeframe;
- Zeitzone;
- Overlays ein/aus.

Pflichtdarstellung:

- Candlesticks;
- VIDYA-Trendlinie gemäß `HIXTON-SPEC-1.0`;
- obere und untere ATR-Bänder;
- farbige Trendsegmente/Füllung;
- Kauf- und Verkaufssignalmarker;
- Einstieg/Ausstieg/Fills;
- offene Position;
- Volumen (`optional sichtbar`, Daten werden dennoch gespeichert);
- Lücken oder nicht verfügbare Bereiche.

Die laufende Kerze erhält z. B. gestrichelte Kontur und Label „vorläufig“. Auf ihr darf kein bestätigter Signalmarker stehen.

### Zeitraumverhalten

| Auswahl | Semantik |
|---|---|
| Heute | 00:00 bis jetzt in gewählter UI-Zeitzone |
| 1 Woche | rollierende letzte 7 × 24 Stunden |
| 1 Monat | rollierende letzte 30 Tage |
| 1 Jahr | rollierende letzte 365 Tage |
| 3 Jahre | rollierende letzte 3 Kalenderjahre bis jetzt |

Standardauswahl ist **1 Monat**. Heute/1W/1M verwenden native `1h`-Bars; 1J wird standardmäßig zu `4h`, 3J zu `1d` aggregiert. Eine verfügbare Auflösung darf manuell gewählt werden. Indikatorwerte und Signalmarker stammen stets aus der nativen `1h`-Strategie; die UI berechnet aus aggregierten Bars keine neuen Signale. Kalenderwoche/-monat sind für V1 ausdrücklich nicht die Semantik.

## Positionen & Orders

Tabellen für:

- aktuelle Positionen;
- offene Orders;
- abgeschlossene Orders/Fills;
- blockierte Intents;
- Reconciliation-Differenzen.

Drill-down von jedem Eintrag zu Signal, Signalkerze, Parametern, Börsenantwort und Logs. Statusfilter und CSV-/JSON-Export sind vorgesehen; Exporte enthalten keine Geheimnisse.

## Backtestseite

Startmaske:

- `Alle 10 Coins`: zehn isolierte Läufe mit je 250 USDT;
- `Einzeltest`: genau ein auswählbares Paar, etwa ETH/USDT, mit 250 USDT;
- optional `Paper-/Live-Spiegel`: 240 USDT gemeinsamer Cashpool mit 3×80-USDT-Slots;
- Zeitraum, Timeframe, Kostenmodell und Strategieversion vor Start sichtbar;
- Backteststart löst niemals eine Börsenorder aus.

Kopf des Reports:

- Run-ID, Status und Erstellzeit;
- Strategie-/Konfigurations-/Datenhash;
- Zeitraum und Warm-up;
- Börse/Datenquelle;
- Gebühren-, Slippage- und Fillmodell;
- zehn Coins und Startkapital;
- Warnung, falls Ergebnis veraltet oder nicht reproduzierbar ist.

Darstellung:

- Kennzahlkarten;
- Equity-/Drawdown-Chart;
- Vergleich mit Buy-and-Hold;
- Monatsrendite-Tabelle;
- Trades und Kosten;
- je Coin Ampel „netto positiv/netto negativ/nicht bewertbar“ ohne Gewinnversprechen;
- Portfolioaggregation ohne schlechte Coins auszublenden.

## Datenqualität

Pro Coin:

- verfügbare Zeitspanne;
- letzte geschlossene Kerze;
- erwartete/vorhandene Bars;
- Lücken, Duplikate, Quarantänefälle;
- letzter erfolgreicher Startup-/Mitternachtsaudit;
- Datenversion;
- Button für sicheren erneuten Audit, nicht für willkürliche Datenmanipulation.

## System & Logs

- Komponentenstatus;
- Scheduler mit nächstem/letztem Lauf;
- Stream-/REST-Status;
- Datenbank/Backup;
- Warnungen und Incidents;
- filterbare strukturierte Logs;
- Korrelations-ID kopierbar;
- klare Hilfetexte für `DEGRADED` und `HALTED`.

## Einstellungen

- Strategieparameter im Livebetrieb standardmäßig schreibgeschützt;
- jede Änderung erzeugt neue Konfigurationsversion und invalidiert betroffene Backtests;
- Secrets werden nur gesetzt/ersetzt, nie im Klartext zurückgelesen;
- Live-Aktivierung erfordert alle Freigabegates, Bestätigung und optional eine Bestätigungsphrase;
- Änderungen zeigen Diff, Zeitpunkt, Benutzer und Begründung.
- Paper-/Live-Positionsgröße startet bei 80 USDT, Slotanzahl bei drei; beide sind später änderbar.
- UI validiert `Slotanzahl × Zielnotional` gegen verfügbares/konfiguriertes Gesamtkapital und aktuelle Binance-Mindestwerte.
- Änderungen wirken nur auf künftige Entries; bestehende Positionen werden nicht automatisch angepasst.
- Einstellungen zeigen die unveränderlichen V1-Baselines: 5 % Tagesverlustpause, 20 % Max-Drawdown-Halt, 25 bp maximale Preisabweichung, 10 Sekunden bis `UNKNOWN` und 30 Sekunden Teilfill-Restfrist.

## Zustände ohne Daten

Die UI muss Loading, leer, stale, teilweise verfügbar, Fehler und Berechtigungsproblem unterscheiden. `0` darf nicht als Ersatz für „unbekannt“ erscheinen.

## Akzeptanz für Chartperformance

- Wechsel zwischen Zeiträumen blockiert die Bedienung nicht dauerhaft.
- Drei Jahre werden downsampled dargestellt, ohne die gespeicherten Backtestdaten zu verändern.
- Marker bleiben zeitlich korrekt.
- Tooltip zeigt OHLCV, Indikatorwerte, Trend, Barstatus und Zeitzone.
