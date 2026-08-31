# 22 – Quellen und Binance-Prüfung

## Zweck

Dieses Dokument hält externe, veränderliche Tatsachen getrennt von dauerhaften Produktentscheidungen fest. Marktstatus, Filter, Gebühren und API-Regeln werden beim späteren Botstart erneut abgefragt; der Stand hier ist kein dauerhaft gültiger Cache.

## Offizielle Binance-Schnittstellen

- Spot REST API – Exchange Information: `https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general`
- Liveendpunkt: `GET https://api.binance.com/api/v3/exchangeInfo`
- Historische Klines: `GET https://api.binance.com/api/v3/klines`

`exchangeInfo` liefert unter anderem Symbolstatus, Spot-Berechtigung, Ordertypen, Preis-/Mengenpräzision, Tick Size, Lot Size und Mindestnotional. Diese Werte sind veränderlich und müssen vor Orderbildung verwendet werden.

## Offizielle Hixton-Produktinformation

- Produktseite: `https://hixton.de/`

Die Seite beschreibt Kauf-/Verkaufspfeile, Nutzung auf verschiedenen Märkten und Timeframes sowie den allgemeinen Risikohinweis, dass keine Gewinngarantie besteht. Sie stellt jedoch keine ausreichend vollständige technische Signalformel oder öffentlich prüfbaren Pine-Source bereit. Für exakte Bot-/Backtestparität gelten deshalb die Beschaffungswege in Dokument 03.

## Prüfung des initialen Universums

Prüfdatum: 31.08.2026. Methode:

1. je Kandidat `exchangeInfo?symbol=<SYMBOL>`;
2. Status muss `TRADING`, Quote `USDT` und Spot-Handel `true` sein;
3. früheste Tageskerze über `klines?symbol=<SYMBOL>&interval=1d&startTime=0&limit=1`;
4. Mindestanforderung: mehr als drei Jahre Binance-Historie vor aktuellem Prüfdatum.

| Symbol | Binance-Status | Spot | früheste gefundene Tagesbar UTC |
|---|---|---:|---|
| BTCUSDT | TRADING | ja | 2017-08-17 |
| ETHUSDT | TRADING | ja | 2017-08-17 |
| BNBUSDT | TRADING | ja | 2017-11-06 |
| SOLUSDT | TRADING | ja | 2020-08-11 |
| XRPUSDT | TRADING | ja | 2018-05-04 |
| ADAUSDT | TRADING | ja | 2018-04-17 |
| LINKUSDT | TRADING | ja | 2019-01-16 |
| AVAXUSDT | TRADING | ja | 2020-09-22 |
| DOTUSDT | TRADING | ja | 2020-08-18 |
| DOGEUSDT | TRADING | ja | 2019-07-05 |

Ergebnis: Alle zehn Kandidaten erfüllen zum Prüfzeitpunkt die technische Mindestbedingung für den dreijährigen Binance-Backtest.

## Bedeutung und Grenze der Coinauswahl

Die Auswahl soll einen etablierten, liquiden und volatilitätsdiversen Testkorb bilden. Sie ist **keine** Aussage, dass diese zehn Coins in zehn Jahren die beste Wertentwicklung haben werden. Das ist nicht seriös vorhersagbar.

Für den Bot gilt:

- Universum vor einem finalen Backtest einfrieren;
- schlechte Ergebnisse nicht nachträglich durch Coinaustausch verstecken;
- Status/Filter bei jedem Start und täglich prüfen;
- Delisting oder Handelspause meldet/pausiert den Coin;
- Ersatz nur nach neuer Entscheidung, Datenprüfung und neuem Vergleichsbacktest;
- jährlicher Review möglich, aber niemals automatische „Top-10“-Rotation.

## Repository-Prüfung

Remote: `https://github.com/127027/Der-Hixton`

Am 31.08.2026 war der Remote per Git erreichbar, lieferte aber noch keine Branch-/Tag-Referenzen. Das entspricht einem neu angelegten, leeren Repository. Vor einem Upload sind Sichtbarkeit, Lizenz und Pine-Veröffentlichungsrecht gemäß Dokument 21 zu klären.
