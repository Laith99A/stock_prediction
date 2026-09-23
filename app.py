"""Streamlit app: analyse stocks and classify them as Kaufen / Halten / Verkaufen.

Start with:  streamlit run app.py
"""
from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from stock_analyzer import charts
from stock_analyzer.backtest import signal_quality, strategy_performance
from stock_analyzer.data import SyntheticProvider, YahooProvider, guess_currency
from stock_analyzer.formatting import LABEL_DE, fmt_date, fmt_days, fmt_num, fmt_pct, fmt_price
from stock_analyzer.market import ScanResult, recommendations_table, scan
from stock_analyzer.recommendation import InsufficientDataError, Recommendation, analyze
from stock_analyzer.scoring import (
    BUY,
    BUY_THRESHOLD,
    COMPONENT_LABELS,
    HOLD,
    SELL,
    SELL_THRESHOLD,
    WEIGHTS,
    compute_scores,
)
from stock_analyzer.universes import BENCHMARKS, UNIVERSES

st.set_page_config(page_title="Aktien-Analyzer", page_icon="📈", layout="wide")

LIVE = "Yahoo Finance (live)"
DEMO = "Demo-Daten (offline)"
CUSTOM = "Eigene Liste"
ICON = {BUY: "🟢", HOLD: "🟡", SELL: "🔴"}


def provider_for(source: str):
    return SyntheticProvider() if source == DEMO else YahooProvider()


@st.cache_data(ttl=3600, show_spinner="Kursdaten werden geladen und analysiert …")
def run_scan(source: str, tickers: tuple[tuple[str, str], ...], benchmark: str, benchmark_name: str,
             period: str) -> ScanResult:
    return scan(provider_for(source), dict(tickers), benchmark or None, benchmark_name, period=period)


@st.cache_data(ttl=3600, show_spinner="Kursdaten werden geladen …")
def load_history(source: str, ticker: str, period: str) -> pd.DataFrame | None:
    return provider_for(source).history([ticker], period=period).get(ticker)


@st.cache_data(ttl=3600, show_spinner="Einzelanalyse wird berechnet …")
def detailed_analysis(df: pd.DataFrame, ticker: str, name: str, benchmark: pd.Series | None):
    scores = compute_scores(df, benchmark)
    rec = analyze(df, ticker, name=name, currency=guess_currency(ticker), benchmark=benchmark,
                  with_triggers=True, scores=scores)
    return rec, scores


def palette() -> dict:
    try:
        return charts.PALETTES["dark" if st.context.theme.type == "dark" else "light"]
    except Exception:
        return charts.PALETTES["light"]


def parse_tickers(text: str) -> list[str]:
    return list(dict.fromkeys(t.upper() for t in re.split(r"[\s,;]+", text) if t))


# --------------------------------------------------------------------------- sidebar

with st.sidebar:
    st.header("Einstellungen")
    source = st.radio("Datenquelle", [LIVE, DEMO], help="Demo-Daten sind simulierte Kurse zum Ausprobieren ohne Internet.")
    universe = st.selectbox("Aktienliste", [*UNIVERSES, CUSTOM])
    if universe == CUSTOM:
        text = st.text_area("Ticker (Yahoo-Format, getrennt durch Komma oder Zeilenumbruch)",
                            "AAPL, MSFT, NVDA, SAP.DE, SIE.DE, ALV.DE", height=100,
                            help="Deutsche Aktien mit Endung .DE (Xetra), z. B. SAP.DE. US-Aktien ohne Endung.")
        tickers = {t: t for t in parse_tickers(text)}
        benchmark = st.selectbox("Vergleichsindex", list(BENCHMARKS), format_func=lambda t: f"{BENCHMARKS[t]} ({t})")
        benchmark_name = BENCHMARKS[benchmark]
    else:
        tickers = UNIVERSES[universe]["tickers"]
        benchmark = UNIVERSES[universe]["benchmark"]
        benchmark_name = UNIVERSES[universe]["benchmark_name"]
    period = st.select_slider("Historie für die Analyse", ["2y", "5y", "10y"], value="5y",
                              format_func=lambda p: p.replace("y", " Jahre"))
    if st.button("🔄 Daten neu laden", width="stretch"):
        st.cache_data.clear()

st.title("📈 Aktien-Analyzer")
st.caption("Kaufen · Halten · Verkaufen – technische Analyse mit Kursziel, Stop-Loss und Zeithorizont. "
           "**Keine Anlageberatung:** Die Signale sind ein Hilfsmittel und keine Garantie für künftige Kurse.")

if not tickers:
    st.info("Bitte mindestens einen Ticker eingeben.")
    st.stop()

try:
    result = run_scan(source, tuple(tickers.items()), benchmark, benchmark_name, period)
except Exception as exc:  # network / rate limit problems from yfinance
    st.error(f"Kursdaten konnten nicht geladen werden: {exc}")
    st.info("Tipp: Internetverbindung prüfen oder links die Datenquelle „Demo-Daten (offline)“ wählen.")
    st.stop()

if not result.recommendations:
    st.error("Für keine der Aktien konnten Kursdaten geladen werden.")
    if result.errors:
        st.write(result.errors)
    st.info("Tipp: Internetverbindung prüfen oder links die Datenquelle „Demo-Daten (offline)“ wählen.")
    st.stop()

if source == DEMO:
    st.warning("Demo-Modus: Die Kurse sind simuliert und haben nichts mit den echten Aktien zu tun.", icon="🧪")

tab_market, tab_detail, tab_method = st.tabs(["📊 Marktübersicht", "🔎 Einzelanalyse", "ℹ️ Methodik"])

# --------------------------------------------------------------------------- market overview

with tab_market:
    regime = result.regime
    recs = result.recommendations
    counts = {label: sum(r.label == label for r in recs) for label in (BUY, HOLD, SELL)}
    cols = st.columns(5)
    if regime is not None:
        cols[0].metric(f"{regime.name}", fmt_num(regime.level), fmt_pct(regime.perf_1m), delta_description="1 Monat")
        cols[1].metric(f"Trend {regime.name}", regime.short_label,
                       "über 200-Tage-Linie" if regime.above_sma200 else "unter 200-Tage-Linie",
                       delta_color="green" if regime.above_sma200 else "red", delta_arrow="off",
                       help="Trend des Vergleichsindex aus 50-/200-Tage-Linie – fließt als Faktor in jeden Score ein")
    else:
        cols[0].metric("Vergleichsindex", "–")
        cols[1].metric("Marktumfeld", "–")
    cols[2].metric("🟢 Kaufen", counts[BUY])
    cols[3].metric("🟡 Halten", counts[HOLD])
    cols[4].metric("🔴 Verkaufen", counts[SELL])

    filter_labels = st.pills("Filter", [LABEL_DE[BUY], LABEL_DE[HOLD], LABEL_DE[SELL]], selection_mode="multi",
                             default=[LABEL_DE[BUY], LABEL_DE[HOLD], LABEL_DE[SELL]], label_visibility="collapsed")

    table = recommendations_table(recs)
    table["Empfehlung"] = [f"{ICON[r.label]} {r.label_de}" for r in recs]
    table["Kurs"] = [fmt_price(r.price, r.currency) for r in recs]
    table = table[["Ticker", "Name", "Empfehlung", "Datum", "Kurs", "Kursziel", "Potenzial", "Stop-Loss", "Score",
                   "Signalstärke", "Seit (Tage)", "Tendenz"]]
    table = table[[r.label_de in (filter_labels or []) for r in recs]]
    table["Datum"] = pd.to_datetime(table["Datum"]).dt.date
    for col in ("Kursziel", "Stop-Loss", "Potenzial"):
        table[col] = pd.to_numeric(table[col], errors="coerce")
    table["Signalstärke"] = table["Signalstärke"] * 100
    table["Potenzial"] = table["Potenzial"] * 100
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        placeholder="–",
        height=min(38 + 35 * len(table), 740),
        column_config={
            "Kurs": st.column_config.TextColumn(),
            "Score": st.column_config.NumberColumn(format="%+.0f", help="−100 (sehr negativ) bis +100 (sehr positiv)"),
            "Signalstärke": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f %%"),
            "Datum": st.column_config.DateColumn(
                "Verkauf ab / Halten bis", format="DD.MM.YYYY",
                help="Kaufen: ab wann der Verkauf empfohlen ist · Halten: ungefähr bis wann halten · "
                     "Verkaufen: frühester Zeitpunkt für eine Neubewertung"),
            "Kursziel": st.column_config.NumberColumn(format="%.2f", help="Take-Profit – nur bei „Kaufen“"),
            "Stop-Loss": st.column_config.NumberColumn(format="%.2f", help="Sofort verkaufen, wenn der Kurs darunter fällt"),
            "Potenzial": st.column_config.NumberColumn(format="%+.1f %%", help="Abstand vom Kurs zum Kursziel"),
            "Seit (Tage)": st.column_config.NumberColumn(help="Wie viele Handelstage das aktuelle Signal schon gilt"),
            "Tendenz": st.column_config.TextColumn(help="Richtung des Scores in den letzten 10 Handelstagen"),
        },
    )
    st.download_button("📥 Tabelle als CSV", recommendations_table(recs).to_csv(index=False, sep=";", decimal=","),
                       file_name="aktien_signale.csv", mime="text/csv")
    if result.errors:
        with st.expander(f"⚠️ {len(result.errors)} Ticker ohne Analyse"):
            for ticker, err in result.errors.items():
                st.write(f"**{ticker}**: {err}")

# --------------------------------------------------------------------------- detail view


def recommendation_card(rec: Recommendation) -> None:
    cur = rec.currency

    def rel(price: float) -> str:
        return fmt_pct(price / rec.price - 1)

    def trigger_text(price: float | None, above: bool, outcome: str) -> str:
        if price is None:
            reach = fmt_pct(8 * rec.atr / rec.price, 0, sign=False)
            return f"{outcome}: derzeit außer Reichweite (dafür wäre eine Kursbewegung von über {reach} nötig)."
        if abs(price / rec.price - 1) < 0.002:
            return f"{outcome}: steht auf der Kippe – schon bei unverändertem Kurs in den nächsten Tagen möglich."
        move = "über" if above else "unter"
        verb = "steigt" if above else "fällt"
        return f"{outcome}, wenn der Kurs innerhalb einer Woche {move} **{fmt_price(price, cur)}** ({rel(price)}) {verb}."

    with st.container(border=True):
        st.markdown(f"### {ICON[rec.label]} {rec.label_de.upper()} · {rec.name} ({rec.ticker})")
        if rec.label == BUY:
            st.markdown(
                f"#### Verkauf empfohlen ab ca. **{fmt_date(rec.horizon_date)}** ({fmt_days(rec.horizon_days)})\n"
                f"- **Früher verkaufen**, sobald das Kursziel **{fmt_price(rec.target_price, cur)}** "
                f"({rel(rec.target_price)}) erreicht ist.\n"
                f"- **Sofort verkaufen**, falls der Kurs unter den Stop-Loss **{fmt_price(rec.stop_loss, cur)}** "
                f"({rel(rec.stop_loss)}) fällt.\n"
                f"- {trigger_text(rec.lower_trigger, False, 'Frühwarnung – das Kaufsignal kippt auf „Halten“')}"
            )
        elif rec.label == HOLD:
            lean = {"steigend": "Der Score steigt – eher Richtung **Kaufen**.",
                    "fallend": "Der Score fällt – eher Richtung **Verkaufen**.",
                    "seitwärts": "Der Score bewegt sich seitwärts."}[rec.tendency]
            st.markdown(
                f"#### Halten bis ca. **{fmt_date(rec.horizon_date)}** ({fmt_days(rec.horizon_days)}), dann neu bewerten\n"
                f"- {trigger_text(rec.upper_trigger, True, '🟢 Kaufsignal')}\n"
                f"- {trigger_text(rec.lower_trigger, False, '🔴 Verkaufssignal')}\n"
                f"- {lean}"
            )
        else:
            st.markdown(
                f"#### Verkaufen bzw. nicht einsteigen – Neubewertung frühestens ca. **{fmt_date(rec.horizon_date)}** "
                f"({fmt_days(rec.horizon_days)})\n"
                f"- {trigger_text(rec.upper_trigger, True, 'Das Verkaufssignal endet')}"
            )
        st.caption(f"Zeithorizont geschätzt aus: {rec.horizon_basis}. Datenstand: {fmt_date(rec.as_of)}.")

    cols = st.columns(5)
    cols[0].metric("Kurs", fmt_price(rec.price, cur))
    cols[1].metric("Signal-Score", f"{rec.score:+.0f}", help="−100 bis +100 · Kaufen ab +25 · Verkaufen ab −25")
    cols[2].metric("Signalstärke", f"{rec.strength * 100:.0f} %",
                   help="Wie deutlich die Schwelle überschritten ist und wie einig sich die Faktoren sind")
    cols[3].metric("Signal aktiv seit", f"{rec.signal_age} Tagen")
    cols[4].metric("Volatilität p. a.", fmt_pct(rec.volatility, sign=False))


with tab_detail:
    options = {r.ticker: f"{r.name} ({r.ticker}) – {ICON[r.label]} {r.label_de}" for r in result.recommendations}
    c1, c2 = st.columns([2, 1])
    selected = c1.selectbox("Aktie aus der Liste", list(options), format_func=options.get)
    free = c2.text_input("… oder beliebigen Ticker eingeben", placeholder="z. B. NVDA oder BMW.DE").strip().upper()

    ticker = free or selected
    name = tickers.get(ticker, ticker)
    df = result.histories.get(ticker)
    if df is None:
        try:
            df = load_history(source, ticker, period)
        except Exception as exc:
            st.error(f"Kursdaten für {ticker} konnten nicht geladen werden: {exc}")
            df = None

    if df is None or df.empty:
        st.error(f"Keine Kursdaten für „{ticker}“ gefunden. Stimmt der Ticker (Yahoo-Format, z. B. SAP.DE)?")
    else:
        try:
            rec, scores = detailed_analysis(df, ticker, name, result.benchmark)
        except InsufficientDataError as exc:
            st.error(str(exc))
        else:
            pal = palette()
            recommendation_card(rec)

            left, right = st.columns([3, 2])
            with left:
                st.subheader("Kursverlauf und Prognose")
                st.plotly_chart(charts.price_chart(df, rec, pal), width="stretch", theme="streamlit")
            with right:
                st.subheader("Begründung")
                icons = {1: "✅", 0: "➖", -1: "⚠️"}
                st.markdown("\n".join(f"- {icons[s]} {text}" for text, s in rec.reasons))
                st.subheader("Faktoren")
                st.plotly_chart(charts.component_chart(rec, pal), width="stretch", theme="streamlit")

            st.subheader("Verlauf des Signal-Scores")
            st.plotly_chart(charts.score_chart(scores, pal), width="stretch", theme="streamlit")

            st.subheader("Rückblick: Wie gut waren die Signale bei dieser Aktie?")
            st.caption("Historischer Test mit denselben Regeln (im Nachhinein berechnet, ohne Gebühren/Steuern). "
                       "Vergangene Treffer sind keine Garantie für die Zukunft.")
            quality = signal_quality(scores, df["Close"])
            strategy = strategy_performance(scores, df["Close"])
            q = quality.rename(index={BUY: "🟢 nach „Kaufen“", HOLD: "🟡 nach „Halten“", SELL: "🔴 nach „Verkaufen“",
                                      "ALL": "Alle Tage"})
            q_display = pd.DataFrame({
                "Tage": q["days"],
                "Ø Kurs 1 Monat später": [fmt_pct(v) for v in q["mean"]],
                "Median": [fmt_pct(v) for v in q["median"]],
                "Anteil im Plus": [fmt_pct(v, 0, sign=False) for v in q["hit_rate"]],
            }, index=q.index.rename("Signal"))
            left, right = st.columns([2, 3])
            with left:
                st.dataframe(q_display, width="stretch")
                m1, m2 = st.columns(2)
                m1.metric("Strategie", fmt_pct(strategy.strategy_return),
                          help="Nur investiert, solange das Signal „Kaufen“ lautet")
                m2.metric("Kaufen & Liegenlassen", fmt_pct(strategy.buy_and_hold_return))
                m1.metric("Max. Verlust (Strategie)", fmt_pct(strategy.strategy_max_drawdown))
                m2.metric("Max. Verlust (Liegenlassen)", fmt_pct(strategy.buy_and_hold_max_drawdown))
                st.caption(f"Zeit investiert: {fmt_pct(strategy.time_in_market, 0, sign=False)} · "
                           f"Anzahl Käufe: {strategy.trades}")
            with right:
                st.plotly_chart(charts.equity_chart(strategy, pal), width="stretch", theme="streamlit")

# --------------------------------------------------------------------------- methodology

with tab_method:
    weights = "\n".join(f"| {COMPONENT_LABELS[k]} | {fmt_num(w * 100, 0)} % |" for k, w in WEIGHTS.items())
    st.markdown(f"""
### So entsteht die Empfehlung

**1. Signal-Score (−100 bis +100).** Für jede Aktie werden täglich sieben Faktoren berechnet und jeweils auf
−1 (sehr negativ) bis +1 (sehr positiv) abgebildet:

| Faktor | Gewicht |
|---|---|
{weights}

Der gewichtete Durchschnitt × 100 ergibt den Roh-Score; geglättet über ca. eine Woche (EMA 5) wird daraus der
**Signal-Score**, damit die Empfehlung nicht täglich hin- und herspringt.

**2. Einstufung.** Score ≥ {BUY_THRESHOLD:+.0f} → 🟢 **Kaufen**, Score ≤ {SELL_THRESHOLD:.0f} → 🔴 **Verkaufen**,
dazwischen 🟡 **Halten**.

**3. Zeithorizont** („Verkauf ab“ bzw. „Halten bis“). Zwei Schätzungen werden gemittelt:
- *Historische Signaldauer:* Wie lange hielten frühere Signale derselben Art bei dieser Aktie noch an, nachdem sie
  so alt waren wie das aktuelle? (Median)
- *Score-Trend:* Der Trend des Scores der letzten 10 Tage wird bis zur nächsten Schwelle fortgeschrieben.

Grenzen: Kaufen 2 Wochen bis 9 Monate, Halten/Verkaufen 1 Woche bis 6 Monate.

**4. Kursziel und Stop-Loss (nur bei Kaufen).**
- *Stop-Loss* = Kurs − 2 × ATR (durchschnittliche Tagesschwankung der letzten 14 Tage).
- *Kursziel* = Fortschreibung des Aufwärtstrends der letzten 6 Monate (zur Vorsicht nur zur Hälfte, maximal
  60 % p. a.) bis zum Verkaufsdatum – mindestens aber Kurs + 3 × ATR (Chance/Risiko ≥ 1,5).

**5. Preis-Schwellen.** Für „Halten“ wird berechnet, bei welchem Kurs der Score die Kauf- bzw. Verkaufsschwelle
kreuzen würde, wenn sich die Aktie innerhalb einer Woche dorthin bewegt. Bei „Kaufen“ zeigt die Frühwarnung, ab
welchem Kurs das Kaufsignal endet.

**6. Marktumfeld.** Der Trend des Vergleichsindex fließt als eigener Faktor ein, ebenso die relative Stärke der
Aktie gegenüber dem Index (3 und 6 Monate).

### Grenzen
- Rein technische Analyse der Kurshistorie – Nachrichten, Bilanzen und Bewertung (KGV usw.) fließen nicht ein.
- Alle Zeitangaben sind grobe Schätzungen. Kursziele und Termine sind **Richtwerte**, keine Prognosen mit Gewähr.
- Datenquelle: Yahoo Finance (dividenden- und splitbereinigte Tagesschlusskurse, ggf. verzögert).
""")
