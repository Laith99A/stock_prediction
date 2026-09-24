# 📈 Aktien-Analyzer – Kaufen · Halten · Verkaufen

Eine App, die Aktien analysiert und jede Aktie in eine von fünf Stufen einordnet – von **Stark kaufen**
bis **Stark verkaufen**. Jeder Fachbegriff wird direkt in der App erklärt.

| Einstufung | Signal-Score | Was die App zusätzlich angibt |
|---|---|---|
| 🟢🟢 **Stark kaufen** (Strong Buy) | ab +55 | wie bei Kaufen |
| 🟢 **Kaufen** (Buy) | +25 bis +55 | **Ab wann der Verkauf empfohlen ist** (Datum), dazu ein **Kursziel** (früher verkaufen, wenn es erreicht ist), ein **Stop-Loss** (sofort verkaufen, wenn der Kurs darunter fällt) und eine Frühwarn-Schwelle, ab der das Kaufsignal endet |
| 🟡 **Halten** (Hold) | −25 bis +25 | **Bis ungefähr wann** halten (Datum der nächsten Neubewertung), dazu die Kurse, ab denen ein Kauf- bzw. Verkaufssignal entstehen würde |
| 🔴 **Verkaufen** (Sell) | −55 bis −25 | Frühester Zeitpunkt für eine Neubewertung und der Kurs, über dem das Verkaufssignal endet |
| 🔴🔴 **Stark verkaufen** (Strong Sell) | bis −55 | wie bei Verkaufen |

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

- **Aktienlisten** (links): Beliebte Aktien, DAX 40, MDAX, Europa, USA Top 100, NASDAQ 100 – zusammen über
  250 Aktien – oder eine eigene Liste mit Namen oder Kürzeln („Alphabet, SAP, Tesla“).
- **🏠 Marktübersicht:** Markttrend des Index, Verteilung der fünf Empfehlungen, Karten mit den Top-Chancen und
  größten Warnsignalen und eine filterbare Tabelle aller Aktien (Klick auf eine Zeile öffnet die Details).
  Export als CSV.
- **🔎 Aktie analysieren:** Suche nach Name oder Kürzel („Alphabet“, „Google“, „SAP“). Nicht in den Listen?
  Einfach den Namen eintippen und mit Enter bestätigen – dann sucht die App bei Yahoo Finance. Du siehst die
  Empfehlung im Klartext („Was heißt das für dich?“), wichtige Kennzahlen, Chart mit Kursziel/Stop-Loss/Datum,
  die Begründung, die sieben Faktoren, den Score-Verlauf und einen Rückblick auf die frühere Trefferquote.
- **📖 Lexikon:** Alle Begriffe (Volatilität, RSI, Stop-Loss, ATR …) einfach erklärt und durchsuchbar. Dieselben
  Erklärungen erscheinen als Tooltip, wenn du über ⓘ-Symbole oder unterstrichene Begriffe fährst.
- Hell- und Dunkelmodus folgen der Einstellung deines Systems (oder dem Menü ⋮ → Settings).
- Ohne Internet: Datenquelle „Demo-Daten (offline)“ wählen (simulierte Kurse zum Ausprobieren).

**Kommandozeile:**

```bash
python -m stock_analyzer                          # DAX 40
python -m stock_analyzer Alphabet SAP NVDA --index ^GSPC
python -m stock_analyzer --liste "USA (Top 100)" --details
python -m stock_analyzer --demo                   # ohne Internet
```

Ticker im Yahoo-Finance-Format: deutsche Aktien mit `.DE` (z. B. `SAP.DE`, `BMW.DE`), US-Aktien ohne Endung.

## So funktioniert die Analyse

1. **Signal-Score von −100 bis +100** aus sieben Faktoren:
   Trend (50-/200-Tage-Linie, 25 %), Momentum (3-/6-Monats-Performance, MACD, 25 %), RSI (10 %),
   Abstand zum 52-Wochen-Hoch (10 %), Volumen/On-Balance-Volume (10 %), relative Stärke zum Index (10 %) und
   Marktumfeld/Index-Trend (10 %). Der Score wird über ca. eine Woche geglättet.
2. **Einstufung:** ab +55 Stark kaufen, ab +25 Kaufen, bis −55 Stark verkaufen, bis −25 Verkaufen,
   dazwischen Halten. Termine, Kursziel und Stop-Loss hängen nur an der Seite (Kauf/Halten/Verkauf): Ein Wechsel
   von „Stark kaufen“ zu „Kaufen“ beendet das Kaufsignal nicht.
3. **Zeithorizont:** Mittelwert aus (a) wie lange gleichartige Signale bei dieser Aktie früher noch anhielten und
   (b) dem aktuellen Trend des Scores bis zur nächsten Schwelle.
4. **Kursziel/Stop-Loss (bei Kaufen):** Stop-Loss = Kurs − 2 × ATR (durchschnittliche Tagesschwankung);
   Kursziel = vorsichtig (halbiert) fortgeschriebener 6-Monats-Trend bis zum Verkaufsdatum, mindestens Kurs + 3 × ATR.
5. **Preis-Schwellen:** Die App rechnet durch, bei welchem Kurs (erreicht innerhalb einer Woche) der Score die
   Kauf- bzw. Verkaufsschwelle kreuzen würde.

Details stehen auch im Tab „⚙️ So funktioniert's“ der App.

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
  ui.py                        Oberflächen-Bausteine (Karten, Score-Skala, Tooltips, CSS)
  glossary.py                  Lexikon: Erklärungen für alle Begriffe
  universes.py                 Aktienlisten, Katalog und Namenssuche
  __main__.py                  Kommandozeilen-Version
tests/                         Tests (pytest)
```

## Entwicklung

```bash
python -m pip install -r requirements-dev.txt
pytest
ruff check .
```
