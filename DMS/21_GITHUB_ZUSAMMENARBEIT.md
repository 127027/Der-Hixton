# 21 – GitHub-Zusammenarbeit

## Repository

- Remote: `https://github.com/127027/Der-Hixton`
- vom Eigentümer für die gemeinsame Arbeit von Codex und GPT vorgesehen;
- Remoteprüfung am 31.08.2026: erreichbar, aber noch ohne sichtbare Git-Referenzen/Commits;
- initialer Dokumentationsstand darf nach ausdrücklicher Freigabe des Eigentümers hochgeladen werden; 99-%-Status wird erst später als eigener Release/Tag gekennzeichnet.

Das lokale OneDrive-Verzeichnis bleibt Arbeitsquelle. GitHub-Synchronisation erfolgt kontrolliert per Commit/Push, niemals unbemerkt durch bloßes Speichern.

## Verbindliche Repository-Struktur

Die vollständige Struktur steht in Dokument 23. Im Hauptordner existiert nur `README.md` als menschlicher Einstieg. Die spätere Anwendung besitzt nur `src/main.py` als technischen Einstieg; Backtest, Paper, Live und UI sind Modi desselben Programms.

```text
README.md              # einziger Projektstart
DMS/
  ... verbindliche Dokumente ...
strategy/
  source_material/
  pine/                # nur wenn Veröffentlichung erlaubt
backtests/
  v1/                  # danach v2, v3 nur bei neuer Methodik
src/
tests/
config/
  examples/          # niemals echte Secrets
.gitignore
LICENSE              # noch zu entscheiden
```

Historische Marktdaten, Datenbanken, große Logs, Backups, API-Schlüssel und lokale Secret-Dateien gehören nicht ins Git-Repository. Lose oder durchnummerierte Startskripte im Hauptordner sind verboten.

## Branch- und Reviewregel

- `main`: nur geprüfte, konsistente Stände;
- Codex-Änderungen: Branch `codex/<kurzes-thema>`;
- GPT-Änderungen: Branch `gpt/<kurzes-thema>`;
- vor Arbeitsbeginn neuesten `main`-Stand holen;
- nicht gleichzeitig dieselbe Datei ohne vorherige Aufteilung bearbeiten;
- jede Änderung nennt betroffene Anforderungs-/Entscheidungs-IDs;
- Pull Request/Review vor Merge in `main`;
- Strategie-, Kapital- oder Orderänderungen benötigen Eigentümerfreigabe;
- Konflikte werden fachlich gelöst, nicht durch blindes Überschreiben.

## Commit-Konvention

Beispiele:

```text
docs(DMS): split paper 3x80 from backtest 10x250
docs(strategy): record DEC-003 timeframe decision
test(parity): add ETH golden bars for pine v1
fix(data): reject provisional candle as signal input
```

Commits sollen klein, nachvollziehbar und thematisch geschlossen sein. Ein DMS-Update und eine davon abweichende Codeänderung dürfen nicht unbemerkt in demselben Commit versteckt werden.

## Quellen der Wahrheit in Git

- `DMS/` beschreibt den freigegebenen Sollzustand.
- Pine-Datei plus SHA-256 definiert die Signallogik.
- Konfigurationsbeispiele enthalten keine echten Schlüssel.
- Dependency-Lock und Codecommit definieren einen Build.
- Backtest-Manifest referenziert Code-, Config- und Datenhash.
- Ein Release-Tag wird erst nach bestandenem Gate gesetzt.

## Geheimnisse und sensible Dateien

Niemals committen:

- Binance API Key/Secret;
- `.env` mit echten Werten;
- Datenbank/Wallet-/Browserprofile;
- Account-, Saldo- oder Steuerexporte mit Identifikatoren;
- Backup-Archive;
- Screenshots mit Secrets;
- private Pine-Quelle, falls Rechte oder Veröffentlichungsfreigabe fehlen.

Vor jedem Push läuft ein Secret-Scan. Ein versehentlich veröffentlichter Schlüssel wird nicht nur aus Git gelöscht, sondern sofort bei Binance gesperrt und rotiert.

## Öffentliche/private Sichtbarkeit und Lizenz

Vor dem ersten Push ist zu bestätigen:

1. Soll das Repository öffentlich oder privat sein?
2. Darf der Hixton-Pine-Quellcode veröffentlicht werden und wem gehören die Rechte?
3. Welche Open-Source- oder proprietäre Lizenz soll gelten?
4. Welche Backtestreports dürfen öffentlich sein?

Ohne diese Antworten wird nur nicht-sensibles DMS vorbereitet; kein Pine-Code und kein Secret wird hochgeladen.

## 99-%-Releasegate

Ein Stand darf vorher als klar gekennzeichneter Arbeitsstand gepusht werden. Ein 99-%-Release/Tag entsteht erst, wenn:

- Pine-Quelle oder zulässige Referenzspezifikation vorhanden;
- kritische Entscheidungen geschlossen;
- DMS-Link-/Konsistenzprüfung grün;
- Eigentümer die Repo-Sichtbarkeit und Pine-Veröffentlichung geklärt hat;
- Secret-Scan grün;
- Release ausdrücklich freigegeben ist.

Jeder Push ist eine externe Änderung und wird als eigener Schritt verifiziert.
