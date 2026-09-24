# 📈 Aktien-Analyzer – Kaufen · Halten · Verkaufen

Eine App, die Aktien analysiert und jede Aktie als **Kaufen**, **Halten** oder **Verkaufen** einstuft.

| Einstufung | Was die App zusätzlich angibt |
|---|---|
| 🟢 **Kaufen** | **Ab wann der Verkauf empfohlen ist** (Datum), dazu ein **Kursziel** (früher verkaufen, wenn es erreicht ist), ein **Stop-Loss** (sofort verkaufen, wenn der Kurs darunter fällt) und eine Frühwarn-Schwelle, ab der das Kaufsignal endet |
| 🟡 **Halten** | **Bis ungefähr wann** halten (Datum der nächsten Neubewertung), dazu die Kurse, ab denen ein Kauf- bzw. Verkaufssignal entstehen würde |
| 🔴 **Verkaufen** | Frühester Zeitpunkt für eine Neubewertung und der Kurs, über dem das Verkaufssignal endet |

> ⚠️ **Keine Anlageberatung.** Die App wertet ausschließlich die Kurshistorie technisch aus. Alle Kursziele und
> Termine sind grobe Richtwerte, keine Garantie für künftige Kurse.

## Installation

Voraussetzung: Python 3.10 oder neuer.

```bash
git clone https://github.com/laith99a/stock_prediction.git
cd stock_prediction
python -m venv .venv
```

Virtuelle Umgebung aktivieren – der Befehl hängt vom Terminal ab:

| Terminal | Befehl |
|---|---|
| Windows **Git Bash** | `source .venv/Scripts/activate` |
| Windows **PowerShell** | `.venv\Scripts\Activate.ps1` |
| Windows **Eingabeaufforderung (cmd)** | `.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

Danach steht `(.venv)` vor der Eingabezeile. Dann die Pakete installieren:

```bash
python -m pip install -r requirements.txt
```

## Starten

**Web-App** (öffnet sich im Browser unter http://localhost:8501):

```bash
streamlit run app.py
```

- Links eine Aktienliste wählen (DAX, US Large Caps, Tech/NASDAQ) oder unter „Eigene Liste“ beliebige Ticker eingeben.
- **Marktübersicht:** Marktumfeld des Index, Anzahl Kaufen/Halten/Verkaufen und eine Tabelle aller Aktien mit
  Empfehlung, Datum („Verkauf ab“ bzw. „Halten bis“), Kursziel, Stop-Loss und Signalstärke. Export als CSV.
- **Einzelanalyse:** Empfehlung im Klartext, Chart mit Kursziel/Stop-Loss/Datum, Begründung, Gewicht der Faktoren,
  Verlauf des Scores und ein Rückblick, wie gut die Signale bei dieser Aktie in der Vergangenheit waren.
- Ohne Internet: Datenquelle „Demo-Daten (offline)“ wählen (simulierte Kurse zum Ausprobieren).

**Kommandozeile:**

```bash
python -m stock_analyzer                          # DAX-Liste
python -m stock_analyzer AAPL MSFT SAP.DE --index ^GSPC
python -m stock_analyzer --liste "US Large Caps" --details
python -m stock_analyzer --demo                   # ohne Internet
```

Ticker im Yahoo-Finance-Format: deutsche Aktien mit `.DE` (z. B. `SAP.DE`, `BMW.DE`), US-Aktien ohne Endung.

## So funktioniert die Analyse

1. **Signal-Score von −100 bis +100** aus sieben Faktoren:
   Trend (50-/200-Tage-Linie, 25 %), Momentum (3-/6-Monats-Performance, MACD, 25 %), RSI (10 %),
   Abstand zum 52-Wochen-Hoch (10 %), Volumen/On-Balance-Volume (10 %), relative Stärke zum Index (10 %) und
   Marktumfeld/Index-Trend (10 %). Der Score wird über ca. eine Woche geglättet.
2. **Einstufung:** Score ≥ +25 → Kaufen, ≤ −25 → Verkaufen, dazwischen Halten.
3. **Zeithorizont:** Mittelwert aus (a) wie lange gleichartige Signale bei dieser Aktie früher noch anhielten und
   (b) dem aktuellen Trend des Scores bis zur nächsten Schwelle.
4. **Kursziel/Stop-Loss (bei Kaufen):** Stop-Loss = Kurs − 2 × ATR (durchschnittliche Tagesschwankung);
   Kursziel = vorsichtig (halbiert) fortgeschriebener 6-Monats-Trend bis zum Verkaufsdatum, mindestens Kurs + 3 × ATR.
5. **Preis-Schwellen:** Die App rechnet durch, bei welchem Kurs (erreicht innerhalb einer Woche) der Score die
   Kauf- bzw. Verkaufsschwelle kreuzen würde.

Details stehen auch im Tab „Methodik“ der App.

## Projektstruktur

```
app.py                         Streamlit-Oberfläche
stock_analyzer/
  data.py                      Kursdaten (Yahoo Finance, Demo-Daten)
  indicators.py                Technische Indikatoren (SMA, RSI, MACD, ATR, …)
  scoring.py                   Faktoren, Score, Einstufung, Preis-Schwellen
  recommendation.py            Empfehlung inkl. Verkaufsdatum, Kursziel, Stop-Loss, Haltedauer
  market.py                    Analyse einer ganzen Aktienliste + Marktumfeld
  backtest.py                  Rückblick auf die historische Signalqualität
  charts.py                    Diagramme
  universes.py                 Vordefinierte Aktienlisten
  __main__.py                  Kommandozeilen-Version
tests/                         Tests (pytest)
```

## Entwicklung

```bash
python -m pip install -r requirements-dev.txt
pytest
ruff check .
```
