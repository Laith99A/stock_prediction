# ☪️ Aktien-Kompass – halal investieren, einfach verstehen

Eine App für junge Einsteiger (18–25), die **halal-konforme Aktien** aus den **USA, Europa und China** findet,
jede Aktie in eine von fünf Stufen einordnet und dabei **jeden Begriff erklärt** – damit du die Sprache der
Investoren lernst.

| Einstufung | Signal-Score | Was die App zusätzlich angibt |
|---|---|---|
| 🟢🟢 **Stark kaufen** (Strong Buy) | ab +55 | wie bei Kaufen |
| 🟢 **Kaufen** (Buy) | +25 bis +55 | **Ab wann der Verkauf empfohlen ist** (Datum), dazu **Kursziel**, **Stop-Loss** und eine Frühwarn-Schwelle |
| 🟡 **Halten** (Hold) | −25 bis +25 | **Bis ungefähr wann** halten, dazu die Kurse, ab denen ein Kauf- bzw. Verkaufssignal entstehen würde |
| 🔴 **Verkaufen** (Sell) | −55 bis −25 | Frühester Zeitpunkt für eine Neubewertung und der Kurs, über dem das Verkaufssignal endet |
| 🔴🔴 **Stark verkaufen** (Strong Sell) | bis −55 | wie bei Verkaufen |

> ⚠️ **Keine Anlageberatung.** Die Empfehlung beruht auf der technischen Analyse des Kursverlaufs, der Halal-Check
> ist eine vereinfachte Prüfung. Alle Kursziele und Termine sind Richtwerte.

## ☪️ Halal-Check

Eine Aktie gilt als **✅ halal**, wenn beide Kriterien erfüllt sind:

1. **Geschäftsfeld:** kein Alkohol, Tabak, Waffen/Rüstung, Glücksspiel/Wetten, keine Banken und Kreditgeschäfte
   (Zinsen), keine konventionellen Versicherungen, kein Schweinefleisch und keine Erwachsenenunterhaltung.
   Grenzfälle, die Gelehrte unterschiedlich bewerten (Musik-/Filmunterhaltung, Krypto, kleine Rüstungsanteile,
   Hotels mit Alkohol), stehen auf **❔ Prüfen**. Die Aktien der App-Listen sind von Hand eingeordnet, andere
   Aktien über die Branche von Yahoo Finance.
2. **Schulden:** **Debt-to-Equity ≤ 0,33** (Schulden höchstens 33 % des Eigenkapitals). Fehlen die Daten, steht
   die Aktie auf **❔ Prüfen**.

Hinweise: Vollständige Shariah-Screenings prüfen zusätzlich z. B. Zinseinnahmen und Bargeldbestände. Viele
islamische Indizes messen die Schulden am Börsenwert statt am Eigenkapital – die Regel der App ist strenger.

## Was die App kann

- **Märkte:** 🔥 Beliebt, 🇺🇸 USA (137 Aktien), 🇪🇺 Europa (126), 🇨🇳 China (49, in Europa handelbar – analysiert mit
  den Kursen der Börse Hongkong), 🌍 Alle Märkte (311) oder ⭐ eine eigene Liste mit Namen oder Kürzeln.
- **🏠 Entdecken:** Aktien als Karten (Preis in €, Mini-Chart der letzten 3 Monate, Halal-Plakette, Empfehlung)
  oder als Tabelle mit KGV, KBV und Debt-to-Equity. Filter für **Preis pro Aktie** (< 20 €, < 50 €, < 100 €),
  **Halal** (nur halal / + prüfen / alle), **Empfehlung**, **Risiko** (ruhig/mittel/wild nach Schwankung),
  **Branche**, **nur mit Dividende**, dazu Suche und Sortierung. Alle Preise werden in Euro umgerechnet.
- **🔎 Analyse:** Suche nach Name oder Kürzel („Alphabet“, „Tencent“, „SAP“). Pro Aktie:
  - **🧾 Überblick:** Halal-Check, Empfehlung im Klartext („Was heißt das für dich?“), wichtigste Zahlen,
    Kurschart mit Kursziel/Stop-Loss/Datum.
  - **📊 Kennzahlen:** KGV, KBV, KUV, PEG, EV/EBITDA, **Debt-to-Equity** (mit Halal-Grenze), Liquidität,
    Eigenkapitalrendite, Margen, Wachstum, Dividende, Beta, Börsenwert – mit Ampel und Faustregel.
  - **🧭 Chart-Leser:** zählt Zeichen für steigende (bullish) und fallende (bearish) Kurse und markiert sie im
    Chart; dazu Volumen, RSI und MACD.
  - **🔬 Hintergrund:** Begründung, sieben Faktoren, Score-Verlauf, Rückblick.
- **🎓 Lernen:** 📚 Chart-Schule (8 Lektionen mit Beispiel-Charts), 📖 Lexikon mit fast 80 Begriffen – inklusive
  **💬 Investor-Sprache** (Bullish/Bearish, Buy the Dip, ATH, FOMO, HODL, ETF, Sparplan …) und **☪️ Halal
  investieren** (Riba, Purification, Schuldengrenze …) – und ein 🧠 Quiz. Auf der Startseite gibt es jeden Tag
  einen **Begriff des Tages**.
- Unterstrichene Wörter und ⓘ-Symbole erklären Begriffe direkt beim Darüberfahren.
- Dunkles Design ohne Seitenleiste; Einstellungen (Datenquelle, Historie) unter ⚙️.

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

```bash
streamlit run app.py
```

Die App öffnet sich im Browser unter http://localhost:8501. Ohne Internet: ⚙️ Einstellungen → „Demo-Daten (offline)“
(simulierte Kurse und Kennzahlen zum Ausprobieren). Beim ersten Laden eines Marktes holt die App die Kennzahlen
aller Aktien (für den Halal-Check) – das dauert einmalig bis zu einer Minute.

**Kommandozeile:**

```bash
python -m stock_analyzer                          # Liste „Beliebt“
python -m stock_analyzer Alphabet SAP Tencent --index ^GSPC
python -m stock_analyzer --liste China --nur-halal   # nur halal-konforme Aktien
python -m stock_analyzer --demo                   # ohne Internet
```

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
6. **Kennzahlen** (Fundamentaldaten von Yahoo Finance) fließen *nicht* in den Score ein – sie ergänzen die
   Chart-Analyse. Die Ampeln folgen allgemeinen Faustregeln; was „teuer“ ist, hängt auch von der Branche ab.
   Yahoo liefert Debt-to-Equity in Prozent (150 = 1,5), die App rechnet das in das übliche Verhältnis um.

Details stehen auch im Tab „⚙️ So funktioniert's“ der App.

## Projektstruktur

```
app.py                         Streamlit-Oberfläche
stock_analyzer/
  data.py                      Kursdaten (Yahoo Finance, Demo-Daten) und Namenssuche
  universes.py                 Märkte USA/Europa/China, Katalog, Flaggen, Suche
  halal.py                     Halal-Check (Geschäftsfeld + Debt-to-Equity ≤ 0,33)
  fx.py                        Umrechnung in Euro
  indicators.py                Technische Indikatoren (SMA, RSI, MACD, ATR, …)
  scoring.py                   Faktoren, Score, Einstufung, Preis-Schwellen
  recommendation.py            Empfehlung inkl. Verkaufsdatum, Kursziel, Stop-Loss, Haltedauer
  fundamentals.py              Kennzahlen (KGV, KBV, Debt-to-Equity …) und Ampel-Bewertung
  chart_reader.py              Chart-Leser: Zeichen für steigende/fallende Kurse
  chart_school.py              Lektionen der Chart-Schule
  learning.py                  Begriff des Tages und Quiz
  glossary.py                  Lexikon: Erklärungen für alle Begriffe
  market.py                    Analyse einer ganzen Liste + Marktumfeld
  backtest.py                  Rückblick auf die historische Signalqualität
  charts.py                    Diagramme
  ui.py                        Design: CSS, Karten, Plaketten, Score-Skala, Tooltips
  __main__.py                  Kommandozeilen-Version
tests/                         Tests (pytest)
```

## Entwicklung

```bash
python -m pip install -r requirements-dev.txt
pytest
ruff check .
```
