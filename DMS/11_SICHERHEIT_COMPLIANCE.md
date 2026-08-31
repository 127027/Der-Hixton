# 11 – Sicherheit und Compliance

## Sicherheitsziele

- keine unbefugten Orders;
- keine Auszahlungsmöglichkeit über den Bot-Key;
- keine Secrets in Dateien, Logs, Screenshots oder Backtestartefakten;
- Manipulationen an Strategie, Konfiguration und Ergebnissen erkennbar;
- kontrollierte Recovery ohne Doppelorders;
- geringstmögliche Rechte.

## API-Schlüssel

- Live verwendet einen eigenen Bot-Account oder Binance-Subaccount; manueller Handel auf genau diesem Account ist verboten;
- eigener API-Key nur für diesen Bot;
- ausschließlich Leserechte und Spot-Handel;
- Withdrawal/Auszahlung deaktiviert;
- Margin/Futures deaktiviert;
- wenn verfügbar IP-Allowlist;
- getrennte Schlüssel für Test/Paper und Live;
- Rotation nach Incident oder regelmäßig gemäß Betriebsentscheidung;
- Schlüsselwerte werden nie in Git, Markdown, YAML-Beispielen oder UI-Export gespeichert.

Erkennt die Reconciliation eine manuelle/Fremdorder oder eine nicht erklärbare Saldenänderung, werden neue Live-Entries global pausiert, bis der Eigentümer den Zustand geklärt und auditiert hat. Der Bot eignet sich nicht zum parallelen Verwalten eines manuell gehandelten Spotbestands.

## Secret-Speicherung

Bevorzugt Betriebssystem-Credential-Store oder dedizierter Secret-Store. Umgebungsvariablen sind nur zulässig, wenn Prozess-, Dump- und Logzugriffe ausreichend geschützt sind. Die UI zeigt höchstens „gesetzt“, Fingerprint/Endziffern und Rotationsdatum.

## Zugriff und lokale Installation

- API standardmäßig nur an localhost binden;
- externe Erreichbarkeit ist gesonderter Scope mit TLS, Auth und Firewall;
- schreibende UI-Aktionen erfordern Authentisierung;
- Sitzungen laufen ab;
- Brute-Force-/Rate-Limit-Schutz für Login und sensitive Aktionen;
- Dateirechte beschränken Datenbank, Logs, Backups und Config auf den Servicebenutzer.

## Integrität und Supply Chain

- Abhängigkeiten werden versioniert und auf bekannte Schwachstellen geprüft;
- Builds sind reproduzierbar soweit praktikabel;
- Strategie-, Config-, Daten- und Berichtshashes werden gespeichert;
- Updates laufen erst in Test/Paper, nicht direkt in Live;
- signierte Releases/Checksums sind für Live vorgesehen;
- DMS und Codeänderungen erhalten Review und Changelog.

## Audit

Auditpflichtig sind:

- Login/Logout und fehlgeschlagene Authentisierung;
- Moduswechsel;
- Aktivieren/Deaktivieren des Tradings;
- Not-Aus und manuelles Schließen;
- API-Key setzen/rotieren (ohne Secretwert);
- Konfigurations- und Strategieänderung;
- Backteststart und -freigabe;
- Datenrevision;
- Order-/Reconciliation-Intervention;
- Backup/Restore.

Auditdaten sind append-only bzw. manipulationsgeschützt und werden nicht über normale UI-Löschfunktionen entfernt.

## Datenschutz

Das System benötigt keine unnötigen personenbezogenen Daten. Account-IDs werden, soweit möglich, pseudonymisiert. Logs/Supportpakete redigieren Tokens, Secrets, vollständige Kontokennungen und ggf. IP-Adressen. Markt-/Backtestdaten, Trade-Ledger, Auditdaten, Incidentberichte und Release-Nachweise bleiben dauerhaft; normale Betriebslogs werden 90 Tage online gehalten und dürfen danach nach dokumentiertem Retention-Job gelöscht werden.

## Rechtliche und finanzielle Grenzen

- Der Bot stellt keine Rendite sicher.
- Historische Ergebnisse sind keine Prognose.
- Gebühren, Steuern, Börsenregeln und lokale rechtliche Anforderungen können sich ändern.
- Vor Livebetrieb sind Nutzungsbedingungen der gewählten Börse, regionale Verfügbarkeit und steuerliche Aufzeichnungspflichten durch den Betreiber zu prüfen.
- Diese DMS ersetzt keine Rechts-, Steuer- oder Anlageberatung.

## Threat-Szenarien

Mindestens testen:

- gestohlener Read/Trade-Key;
- manipulierte Konfigurationsdatei;
- Replay einer Orderanfrage;
- gefälschte/verspätete Marktdaten;
- UI-CSRF bzw. unberechtigter Moduswechsel;
- Log-Injection/Secret-Leak;
- Abhängigkeit mit Schadcode;
- kompromittiertes Backup;
- DoS/Rate-Limit mit stale Daten;
- lokaler Benutzer ändert DB-Zustand.

## Live-Freigabebedingung

Live bleibt technisch gesperrt, bis mindestens Secretschutz, Least Privilege, Reconciliation, Idempotenz, Not-Aus, Audit, Backup/Restore, Paper-Soak-Test und Incident-Runbook bestanden sind.
