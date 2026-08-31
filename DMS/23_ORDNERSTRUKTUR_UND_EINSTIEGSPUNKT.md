# 23 – Ordnerstruktur und einziger Einstiegspunkt

## Verbindliches Prinzip

Das Projekt besitzt genau **eine zentrale menschliche Startdatei** im Repository: `/README.md`.

Die spätere Anwendung besitzt genau **einen technischen Einstiegspunkt**: `/src/main.py` oder ein einziges daraus gebautes Kommando. Backtest, Paper und Live werden als Modi dieses Einstiegs ausgeführt. Es werden keine parallelen Hauptskripte wie `start_backtest.py`, `paper_bot.py`, `live_bot.py`, `run_ui.py` oder durchnummerierte Kopien im Hauptordner angelegt.

## Verbindliche Struktur

```text
Der-Hixton/
├── README.md                         # einziger Projektstart
├── .gitignore
├── DMS/                              # verbindliche Dokumentation
├── strategy/
│   ├── source_material/              # unveränderte Eingangsquellen
│   └── pine/                         # freigegebene Pine-Referenz, falls erlaubt
├── backtests/
│   ├── v1/
│   │   ├── manifest-template.yaml
│   │   ├── runs/                     # konkrete Run-IDs
│   │   ├── reports/                  # freigegebene Berichte
│   │   ├── trades/                   # kleine/sanitisierte Tradeexports
│   │   └── data_quality/             # Qualitätsnachweise
│   ├── v2/                           # erst bei neuer Methodik anlegen
│   └── v3/                           # erst bei Bedarf anlegen
├── config/
│   └── examples/                     # secretfreie Beispiele
├── src/                              # spätere Anwendung
│   └── main.py                       # später einziger technischer Einstieg
└── tests/                            # Tests, Golden-Daten und Fixtures
```

Nicht versionierte Laufzeitdaten liegen später in ignorierten Verzeichnissen wie `data/`, `runtime/`, `logs/` und `backups/`.

## Ein einziger Programmstart

Vorgesehene spätere Bedienform:

```text
hixton backtest --version v1 --all
hixton backtest --version v1 --symbol ETHUSDT
hixton paper
hixton live
hixton ui
```

Alle Befehle führen intern über denselben Einstieg und dieselbe Konfigurations-/Strategieengine. `live` bleibt technisch gesperrt, bis die Live-Gates bestanden sind. Die Beispiele beschreiben nur die Zielstruktur; sie implementieren noch keinen Bot.

## Backtestversionierung

- `backtests/v1`: erste freigegebene Backtestmethodik.
- `backtests/v2`: nur bei fachlicher Änderung, beispielsweise neuem Fill-/Kostenmodell oder geänderter Strategieversion.
- `backtests/v3`: nächste fachliche Änderung.
- Reine Wiederholung mit gleichen Regeln erhält innerhalb derselben Version eine neue unveränderliche Run-ID unter `runs/`.
- Ein gültiger Run wird nicht überschrieben oder nachträglich „verbessert“.
- Jede Version referenziert Code-, Pine-, Config- und Datenhash.
- Versionen werden numerisch ohne Fantasienamen geführt.

## Was nicht in den Hauptordner gehört

- Kopien wie `bot_final.py`, `bot_final2.py`, `bot_neu.py`;
- zehn coinbezogene Startdateien;
- separate Backtest-Engines je Coin;
- lose Reports oder CSV-Dateien;
- API-Keys, `.env`, Datenbanken, Marktdaten oder Logs;
- temporäre GPT-/Codex-Arbeitsdateien.

## Neue Datei oder neuer Ordner

Vor dem Anlegen wird geprüft:

1. Hat die Datei eine eindeutige Verantwortung?
2. Gibt es bereits einen richtigen Zielordner?
3. Ist sie eine Quelle, Konfiguration, Testfixture, Laufzeitdatei oder Ergebnisartefakt?
4. Erzeugt sie einen zweiten Einstiegspunkt? Dann ist sie abzulehnen.
5. Muss sie überhaupt in Git oder gehört sie in einen ignorierten Laufzeitordner?

Diese Regel gilt gleichermaßen für Codex, GPT und manuelle Änderungen.

