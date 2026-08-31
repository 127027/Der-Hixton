# 16 – Entscheidungslog und offene Punkte

Dieses Dokument ist die einzige Sammelstelle für offene fachliche Entscheidungen. „Default des Frameworks“ ist keine Entscheidung.

## P0 – vor exakter Signalparität und belastbarem Backtest

| ID | Frage/fehlendes Artefakt | Aktuelle Annahme | Auswirkung |
|---|---|---|---|
| DEC-001 | Vollständiger Pine-v6-Quellcode inklusive Inputs? | fehlt | Keine exakte Strategie oder 99-%-Freigabe möglich |
| DEC-002 | Pine-Parameterwerte und Source? | fehlen | Indikatorwerte/Signale unbestimmt |
| DEC-003 | Trading-Timeframe? | offen; UI-Zeiträume sind davon unabhängig | Datenmenge, Signalspeed, Gebühren, Warm-up |
| DEC-004 | Welche Börse/Datenquelle und welches Konto? | **BESCHLOSSEN: Binance Spot/USDT**; konkretes Paper-/Live-Konto noch offen | API, Historie, Filter, Gebühren, rechtliche Verfügbarkeit |
| DEC-005 | Exakte zehn Coins? | **BESCHLOSSEN FÜR V0.1:** BTC, ETH, BNB, SOL, XRP, ADA, LINK, AVAX, DOT, DOGE gegen USDT | Daten/Backtests/Portfolio |
| DEC-006 | Gibt es ein festes 3-Jahres-Gewinnziel? | **BESCHLOSSEN: nein**; Backtest prüft Reaktion und berichtet Ergebnis ohne 250-/500-Ziel | Ergebnisinterpretation |
| DEC-007 | Nur Long oder echte Shorts? | Spot long-only; Verkauf = Long schließen | Execution, Risiko, Börsenprodukt |
| DEC-008 | Kapital-/Positionsmodell? | **BESCHLOSSEN:** Backtest 10×250 plus Einzeltest 250; Paper/Live 240 mit 3×80; kein automatisches Compounding gemäß DEC-030 | PnL, Slots und Drawdown |
| DEC-009 | Ordertyp live? | Market mit Schutz angenommen | Fill, Slippage, Timeoutlogik |
| DEC-010 | Gebührenstufe und Slippagemodell? | fehlt | Kein valider Netto-Backtest |
| DEC-011 | Bar-Close/Initialtrend/Warm-up exakt aus Pine? | sichere Zustandsmaschine angenommen | erste Signale und Parität |
| DEC-029 | Welche drei Signale erhalten Slots, wenn mehr Coins gleichzeitig kaufen wollen? | **BESCHLOSSEN:** stärkster normalisierter Hixton-Ausbruch; Gleichstand über feste Coin-Tie-Break-Reihe | Portfolioresultat |
| DEC-030 | Bleibt ein Slot fest 80 USDT oder wächst er mit Gewinnen? | **BESCHLOSSEN:** 80 USDT fest bis zu einer bewussten, auditierbaren UI-Änderung; kein automatisches Compounding | Compounding/Profit/Risiko |

## Aktuell verbleibende Kernblocker

Für Implementierung, Signalparität und einen belastbaren Nettobacktest bleiben nur diese drei Themenblöcke zwingend offen:

1. **Pine-Referenz (`DEC-001`, `DEC-002`, `DEC-011`):** vollständiger zulässiger Pine-Code oder gleichwertige technische Spezifikation mit Referenzwerten; Inputs, Initialzustand und Warm-up daraus ableiten.
2. **Trading-Timeframe (`DEC-003`):** eine feste Signalkerzenauflösung wählen; UI-Zeiträume bleiben davon unabhängig.
3. **Kostenmodell (`DEC-010`):** Binance-Gebührenstufe und realistisches Slippage-/Spreadmodell für Nettoergebnisse festlegen.

`DEC-029` und `DEC-030` sind geschlossen. Die übrigen P1-/P2-Punkte blockieren nicht die erste Signalengine bzw. den technischen Bruttobacktest; sie werden vor Paper- oder Live-Freigabe geschlossen.

## P1 – vor Paper-/Livebetrieb

| ID | Entscheidung | Vorschlag |
|---|---|---|
| DEC-012 | täglicher Job in welcher Zeitzone? | 00:05 UTC; UI zeigt Europe/Berlin |
| DEC-013 | Stale-data-Grenze | abhängig vom Timeframe, z. B. deutlich kleiner als ein Barintervall |
| DEC-014 | Maximal erlaubte Preisabweichung/Slippage | aus Paperdaten ableiten und bestätigen |
| DEC-015 | Tagesverlust-/Drawdown-Pause | nur neue Entries pausieren; Werte festlegen |
| DEC-016 | Teilfill-Rest/Order-Timeout | keine Neuorder ohne Statusklärung; konkrete Frist offen |
| DEC-017 | Umgang mit offener Position am Backtestende | mark-to-market separat, nicht künstlich fillen |
| DEC-018 | Paper-Soak-Dauer | mindestens mehrere Wochen und genügend Barwechsel; nach Timeframe festlegen |
| DEC-019 | Alarmkanal | lokale UI plus externer Kanal für P1/P2 nötig |
| DEC-020 | Backupziel und Retention | getrennt vom Rechner, verschlüsselt, Restore regelmäßig testen |
| DEC-021 | Darf derselbe Börsenaccount manuell gehandelt werden? | nein; eigener Bot-Subaccount bevorzugt |
| DEC-022 | lokale UI oder Netzwerkzugriff? | localhost-only |
| DEC-023 | Autostart/Windows-Service? | ja für unbeaufsichtigten Betrieb, erst nach Paperfreigabe |
| DEC-031 | GitHub-Repository öffentlich oder privat; darf Pine-Source hinein? | vor Upload prüfen; Secrets niemals, Pine nur mit Eigentums-/Lizenzfreigabe |

## P2 – Produktpolitur

| ID | Entscheidung | Vorschlag |
|---|---|---|
| DEC-024 | Exportformate | CSV + JSON + druckbarer HTML/PDF-Report |
| DEC-025 | UI-Standardzeitraum | 1 Monat |
| DEC-026 | UI-Chart-Aggregation je Bereich | automatisch, aber sichtbar und manuell wählbar |
| DEC-027 | Daten-/Log-Retention | Backtestdaten dauerhaft; Logs rotierend gemäß Auditbedarf |
| DEC-028 | Sprache | Deutsch zuerst; technische Werte/IDs unverändert |

## Vorläufige Beschlüsse aus dem Nutzerauftrag

| Beschluss | Status |
|---|---|
| kein Botbau in diesem Auftrag, nur Dokumentation | VERBINDLICH |
| zehn Kryptowährungen | VERBINDLICH |
| Binance Spot/USDT | VERBINDLICH |
| Backtest-Batch: zehn isolierte Tests à 250 USDT | VERBINDLICH |
| Backtest-Einzelmodus: frei wählbarer Coin, z. B. ETH, mit 250 USDT | VERBINDLICH |
| Paper 24/7 als Vorbereitung für Live | VERBINDLICH |
| Paper-/Live-Start: gemeinsamer Cashpool 240 USDT, drei Slots à 80 USDT | VERBINDLICH |
| kein festes 250-/500-USDT-Performanceziel | VERBINDLICH |
| dreijähriger Primärbacktest | VERBINDLICH |
| UI-Charts Heute/1W/1M/1J/3J | VERBINDLICH |
| lokale heruntergeladene Historie nutzen | VERBINDLICH |
| Startup prüft und aktualisiert alle zehn Coins | VERBINDLICH |
| tägliche Aktualisierung um Mitternacht | VERBINDLICH; exakte Zeitzone/Uhrminute ANNAHME |
| alles basiert auf dem Hixton-Indikator | VERBINDLICH |
| GitHub-Repository `127027/Der-Hixton` ist die zentrale Projektablage; Arbeitsstände werden gepusht, 99 % ist ein separates Releasegate | VERBINDLICH |

## Erklärung zu DEC-001: Was ist der Pine-Code?

Der Pine-Code ist der **vollständige Quelltext des TradingView-Indikators**, nicht nur seine Beschreibung. Er beginnt typischerweise mit `//@version=5` oder `//@version=6` und enthält Zeilen wie `indicator(...)`, Inputs, VIDYA-/ATR-Berechnung und Kauf-/Verkaufsbedingungen.

So wird er beschafft, wenn der Quelltext zugänglich ist:

1. Indikator in TradingView öffnen.
2. Unten den „Pine Editor“ öffnen.
3. gesamten Inhalt kopieren, einschließlich Versionszeile.
4. als Datei, zum Beispiel `hixton_indicator.pine`, bereitstellen.
5. zusätzlich Screenshot/Export aller aktuell verwendeten Indikatoreinstellungen und den verwendeten Chart-Timeframe liefern.

Ist der Indikator „protected/invite-only“ und der Editor zeigt keinen Source, darf der Code nicht erraten oder unzulässig beschafft werden. Dann benötigen wir vom Rechteinhaber den Source oder ersatzweise eine offizielle, ausreichend genaue Spezifikation plus exportierte Referenzwerte/Signale. Ohne eines davon kann keine 1:1-Parität bewiesen werden.

## Entscheidungsformat

Nach Bestätigung wird jeder Eintrag so ergänzt:

```text
Entscheidung: DEC-xxx
Datum/Zeitzone:
Entschieden von:
Beschluss:
Begründung:
Betroffene Anforderungen/Dokumente:
Neue Strategie-/Konfigurationsversion:
```

## Empfohlene nächste Rückfrage an GPT/den Eigentümer

Die effizienteste Antwort ist ein Paket aus:

1. vollständigem Pine-Code als Datei;
2. gewünschtem Trading-Timeframe;
3. Binance-Gebührenstufe bzw. ob Gebühren mit BNB bezahlt werden;
4. Bestätigung „Spot long-only, Verkauf schließt Position, kein Short“ oder einer abweichenden Regel;
5. gewünschter Live-Ordertyp;
6. Slotpriorisierung bei mehr als drei gleichzeitigen Kaufkandidaten;
7. feste 80 USDT oder automatisches Compounding;
8. Bestätigung, ob das GitHub-Repository öffentlich oder privat sein soll und ob der Pine-Code dort veröffentlicht werden darf.
