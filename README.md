# Der Hixton Trading Bot

Dies ist die **einzige zentrale Startdatei** des Projekts.

Zentrale Projektablage: `https://github.com/127027/Der-Hixton`

Aktueller Status: **DMS V1 ist fachlich eingefroren und implementierbar.** Es wurde weiterhin kein Trading-Bot implementiert und kein valider Backtest ausgeführt; diese Nachweise entstehen erst nach einem separaten Bauauftrag.

## Wo anfangen?

1. Verbindliche DMS-Einführung: [`DMS/00_DOKUMENTENLENKUNG_UND_START.md`](DMS/00_DOKUMENTENLENKUNG_UND_START.md)
2. Geschlossene Entscheidungen und Änderungsregeln: [`DMS/16_ENTSCHEIDUNGSLOG_UND_OFFENE_PUNKTE.md`](DMS/16_ENTSCHEIDUNGSLOG_UND_OFFENE_PUNKTE.md)
3. Ordner- und Einstiegspunktregel: [`DMS/23_ORDNERSTRUKTUR_UND_EINSTIEGSPUNKT.md`](DMS/23_ORDNERSTRUKTUR_UND_EINSTIEGSPUNKT.md)

## Zwei Laufwelten

- `BACKTEST`: zehn isolierte Tests à 250 USDT oder ein frei wählbarer Einzeltest mit 250 USDT.
- `PAPER/LIVE`: 24/7-System, anfangs 240 USDT gemeinsamer Cashpool und drei Slots à 80 USDT. Live bleibt bis zur späteren Freigabe deaktiviert.

## Eine Startlogik

Die spätere Anwendung erhält genau einen Einstiegspunkt: `src/main.py` bzw. ein daraus bereitgestelltes Kommando. Backtest, Paper und Live sind Modi dieses einen Einstiegs. Weitere `start_*.py`, `run_*.py` oder konkurrierende Hauptprogramme sind nicht zulässig.

## Backtest-Versionen

Backtestmethoden und freigegebene Ergebnisstände liegen ausschließlich unter:

```text
backtests/v1/
backtests/v2/
backtests/v3/
```

Eine neue fachliche Methodik erhält die nächste Version. Ein veröffentlichter gültiger Stand wird nicht überschrieben.

## Wichtige Regeln

- Binance Spot, USDT-Paare, kein Leverage gemäß aktuellem DMS.
- Keine API-Schlüssel, Secrets, Datenbanken oder privaten Kontodaten in Git.
- Kein GitHub-Stand ersetzt die DMS-Freigabe.
- Normative V1-Strategie ist `HIXTON-SPEC-1.0`; fremder/proprietärer Pine-Quellcode wird ohne nachgewiesene Rechte nicht veröffentlicht.
- Historische Ergebnisse sind keine Gewinngarantie.
