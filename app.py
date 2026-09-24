"""Streamlit app: analyse stocks and classify them from "Stark kaufen" to "Stark verkaufen".

Start with:  streamlit run app.py
"""
from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from stock_analyzer import charts, ui
from stock_analyzer.backtest import signal_quality, strategy_performance
from stock_analyzer.data import SyntheticProvider, YahooProvider, guess_currency, search_yahoo
from stock_analyzer.formatting import LABEL_DE, fmt_date, fmt_num, fmt_pct, fmt_price, fmt_score, label_text
from stock_analyzer.glossary import CATEGORIES, TERMS, tip
from stock_analyzer.market import ScanResult, recommendations_table, scan
from stock_analyzer.recommendation import InsufficientDataError, analyze
from stock_analyzer.scoring import (
    BUY,
    BUY_THRESHOLD,
    COMPONENT_LABELS,
    HOLD,
    LABELS,
    SELL,
    SELL_THRESHOLD,
    STRONG_BUY_THRESHOLD,
    STRONG_SELL_THRESHOLD,
    WEIGHTS,
    classify,
    compute_scores,
)
from stock_analyzer.universes import BENCHMARKS, CATALOG, UNIVERSES, search_catalog

st.set_page_config(page_title="Aktien-Analyzer", page_icon="📈", layout="wide")

LIVE = "Live-Kurse (Yahoo Finance)"
DEMO = "Demo-Daten (offline)"
CUSTOM = "✏️ Eigene Liste"
CARD = {"border": True, "height": "stretch"}  # metric tiles as equal-height cards
TAB_MARKET, TAB_STOCK, TAB_GLOSSARY, TAB_HOW = "🏠 Marktübersicht", "🔎 Aktie analysieren", "📖 Lexikon", "⚙️ So funktioniert's"


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


@st.cache_data(ttl=24 * 3600, show_spinner="Suche bei Yahoo Finance …")
def yahoo_search(query: str) -> list[dict[str, str]]:
    return search_yahoo(query)


def theme_type() -> str | None:
    try:
        return st.context.theme.type
    except Exception:
        return None


def palette() -> dict:
    return charts.PALETTES["dark" if theme_type() == "dark" else "light"]


def html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def resolve_entries(text: str, live: bool) -> dict[str, str]:
    """Turn a comma separated list of names or tickers into {ticker: name}."""
    out: dict[str, str] = {}
    for entry in (e.strip() for e in re.split(r"[,;\n]+", text)):
        if not entry:
            continue
        upper = entry.upper()
        hits = search_catalog(entry, 1)
        if upper in CATALOG:
            out[upper] = CATALOG[upper]
        elif hits:
            out[hits[0][0]] = hits[0][1]
        elif live and (" " in entry or entry != upper) and (found := yahoo_search(entry)):
            out[found[0]["ticker"]] = found[0]["name"]
        else:
            for token in upper.split():
                out[token] = token
    return out


def open_stock(ticker: str) -> None:
    """Callback: show a stock in the analysis tab."""
    st.session_state.stock = ticker
    st.session_state.nav = TAB_STOCK


# --------------------------------------------------------------------------- sidebar

with st.sidebar:
    html('<div style="font-size:1.35rem;font-weight:800;margin-bottom:2px">📈 Aktien-Analyzer</div>'
         '<div class="muted" style="font-size:.88rem;margin-bottom:10px">Kaufen · Halten · Verkaufen – einfach erklärt</div>')
    universe = st.selectbox(
        "Aktienliste", [*UNIVERSES, CUSTOM],
        format_func=lambda u: u if u == CUSTOM else f"{u} · {len(UNIVERSES[u]['tickers'])} Aktien",
        help="Welche Aktien in der Marktübersicht analysiert werden. Einzelne Aktien findest du jederzeit "
             "im Tab „Aktie analysieren“ über die Suche.")
    source = st.radio("Datenquelle", [LIVE, DEMO],
                      help="Live-Kurse kommen von Yahoo Finance (Tagesschlusskurse). Demo-Daten sind simulierte "
                           "Kurse zum Ausprobieren ohne Internet.")
    if universe == CUSTOM:
        text = st.text_area("Deine Aktien (Namen oder Kürzel, mit Komma getrennt)",
                            "Apple, Microsoft, Alphabet, NVIDIA, SAP, Siemens, Allianz, Rheinmetall", height=110,
                            help="Zum Beispiel „Alphabet, SAP, Tesla“ oder Kürzel wie GOOGL, SAP.DE, TSLA.")
        tickers = resolve_entries(text, live=source == LIVE)
        benchmark = st.selectbox("Vergleichsindex", list(BENCHMARKS), format_func=lambda t: BENCHMARKS[t],
                                 help=tip("index"))
        benchmark_name = BENCHMARKS[benchmark]
    else:
        tickers = UNIVERSES[universe]["tickers"]
        benchmark = UNIVERSES[universe]["benchmark"]
        benchmark_name = UNIVERSES[universe]["benchmark_name"]
    period = st.select_slider("Historie für die Analyse", ["2y", "5y", "10y"], value="5y",
                              format_func=lambda p: p.replace("y", " Jahre"),
                              help="Wie viele Jahre Kursverlauf ausgewertet werden. Mehr Historie = bessere "
                                   "Schätzung der Signaldauer, aber langsameres Laden.")
    if st.button("🔄 Kurse neu laden", width="stretch"):
        st.cache_data.clear()
    st.divider()
    st.caption("⚠️ **Keine Anlageberatung.** Die App wertet nur den Kursverlauf aus. Kursziele und Termine "
               "sind Richtwerte, keine Garantie.")

html(ui.css(theme_type()))

if not tickers:
    st.info("Bitte mindestens eine Aktie eingeben.")
    st.stop()

try:
    result = run_scan(source, tuple(tickers.items()), benchmark, benchmark_name, period)
except Exception as exc:  # network / rate limit problems from yfinance
    st.error(f"Kursdaten konnten nicht geladen werden: {exc}")
    st.info("Tipp: Internetverbindung prüfen oder links die Datenquelle „Demo-Daten (offline)“ wählen.")
    st.stop()

if not result.recommendations:
    st.error("Für keine der Aktien konnten Kursdaten geladen werden.")
    st.info("Tipp: Internetverbindung prüfen oder links die Datenquelle „Demo-Daten (offline)“ wählen.")
    st.stop()

recs = result.recommendations
as_of = max(r.as_of for r in recs)
html(ui.hero(
    "Aktien-Analyzer",
    "Kaufen, halten oder verkaufen?",
    f"{len(recs)} Aktien analysiert – jede mit klarer Empfehlung, Verkaufsdatum, Kursziel und Stop-Loss. "
    "Fahre mit der Maus über unterstrichene Begriffe, um sie erklärt zu bekommen.",
    [("🧪 Demo-Daten" if source == DEMO else "📡 Live · Yahoo Finance"), f"📅 Stand {fmt_date(as_of)}",
     f"📋 {universe.replace('✏️ ', '')}"],
))
if source == DEMO:
    st.warning("Demo-Modus: Die Kurse sind simuliert und haben nichts mit den echten Aktien zu tun.", icon="🧪")

tabs = st.tabs([TAB_MARKET, TAB_STOCK, TAB_GLOSSARY, TAB_HOW], key="nav", on_change="rerun")

# --------------------------------------------------------------------------- market overview

with tabs[0]:
    with st.expander("👋 Neu hier? So liest du die App", expanded=False):
        html(ui.steps([
            ("Empfehlung ansehen", "Jede Aktie bekommt eine von fünf Stufen – von 🟢🟢 Stark kaufen bis 🔴🔴 Stark "
                                   "verkaufen. Grundlage ist der Signal-Score von −100 bis +100."),
            ("Datum beachten", "Bei „Kaufen“ steht dort, <b>ab wann der Verkauf empfohlen ist</b>, bei „Halten“, "
                               "<b>bis wann ungefähr</b> du halten solltest."),
            ("Details & Begriffe", "Klicke auf eine Aktie für Charts, Kursziel und Stop-Loss. Unbekannte Begriffe "
                                   "erklären die ⓘ-Symbole und der Tab „📖 Lexikon“."),
        ]))

    regime = result.regime
    counts = {label: sum(r.label == label for r in recs) for label in LABELS}
    buy_share = sum(r.side == BUY for r in recs) / len(recs)
    c = st.columns(4)
    if regime is not None:
        c[0].metric(regime.name, fmt_num(regime.level), fmt_pct(regime.perf_1m), delta_description="1 Monat",
                    **CARD, help=tip("index"))
        c[1].metric("Markttrend", regime.short_label,
                    "über 200-Tage-Linie" if regime.above_sma200 else "unter 200-Tage-Linie",
                    delta_color="green" if regime.above_sma200 else "red", delta_arrow="off", **CARD,
                    help=tip("marktumfeld"))
    else:
        c[0].metric("Vergleichsindex", "–", **CARD)
        c[1].metric("Markttrend", "–", **CARD)
    c[2].metric("Aktien mit Kaufsignal", f"{sum(r.side == BUY for r in recs)} von {len(recs)}",
                f"{buy_share:.0%} der Liste", delta_arrow="off", delta_color="gray", **CARD,
                help="Wie viele Aktien der Liste auf „Kaufen“ oder „Stark kaufen“ stehen – ein Stimmungsbild des Markts.")
    avg = sum(r.score for r in recs) / len(recs)
    c[3].metric("Ø Signal-Score", fmt_score(avg), f"entspricht „{LABEL_DE[classify(avg)]}“", delta_arrow="off",
                delta_color="gray", **CARD, help=tip("score"))

    html(ui.section("Verteilung der Empfehlungen"))
    html(f'<div class="card">{ui.distribution_bar(counts)}</div>')

    def card_row(title: str, subtitle: str, items, empty: str, key: str) -> None:
        html(ui.section(title, subtitle))
        if not items:
            st.info(empty)
            return
        cols = st.columns(4)
        for col, rec in zip(cols, items):
            with col:
                html(ui.stock_card(rec))
                st.button("Details ansehen →", key=f"{key}-{rec.ticker}", on_click=open_stock, args=(rec.ticker,),
                          width="stretch")

    card_row("🔥 Top-Chancen", "Die Aktien mit dem höchsten Score auf der Kauf-Seite",
             [r for r in recs if r.side == BUY][:4], "Aktuell hat keine Aktie der Liste ein Kaufsignal.", "top")
    card_row("⚠️ Größte Warnsignale", "Die Aktien mit dem niedrigsten Score auf der Verkaufs-Seite",
             [r for r in reversed(recs) if r.side == SELL][:4], "Aktuell hat keine Aktie der Liste ein Verkaufssignal.",
             "flop")

    html(ui.section("Alle Aktien", "Tipp: Klicke auf eine Zeile, um die Aktie im Detail zu sehen."))
    chosen = st.pills("Empfehlung filtern", [label_text(k) for k in LABELS], selection_mode="multi",
                      default=[label_text(k) for k in LABELS], label_visibility="collapsed")
    query = st.text_input("Suchen", placeholder="🔍 Aktie in der Liste suchen …", label_visibility="collapsed",
                          width=420)

    table = recommendations_table(recs)
    mask = table["Empfehlung"].isin(chosen or [])
    if query:
        q = query.casefold()
        mask &= table["Name"].str.casefold().str.contains(q, regex=False) | table["Ticker"].str.casefold().str.contains(
            q, regex=False)
    table = table[mask].reset_index(drop=True)
    st.session_state.table_tickers = list(table["Ticker"])
    view = table.copy()
    view["Kurs"] = [fmt_price(p, cur) for p, cur in zip(view["Kurs"], view["Währung"])]
    for col in ("Kursziel", "Stop-Loss", "Potenzial"):
        view[col] = pd.to_numeric(view[col], errors="coerce")
    view["Potenzial"] = view["Potenzial"] * 100
    view["Signalstärke"] = view["Signalstärke"] * 100
    view["Score"] = view["Score"].astype(int)  # truncated like fmt_score, so it matches the category
    view["Datum"] = pd.to_datetime(view["Datum"]).dt.date

    def on_table_select() -> None:
        rows = st.session_state.stock_table.selection.rows
        if rows:
            open_stock(st.session_state.table_tickers[rows[0]])

    st.dataframe(
        view,
        hide_index=True,
        width="stretch",
        height=min(40 + 35 * len(view), 740),
        placeholder="–",
        key="stock_table",
        on_select=on_table_select,
        selection_mode="single-row",
        column_order=["Name", "Ticker", "Empfehlung", "Score", "Datum", "Kurs", "Kursziel", "Potenzial",
                      "Stop-Loss", "Signalstärke", "Seit (Tage)", "Tendenz"],
        column_config={
            "Name": st.column_config.TextColumn("Aktie", pinned=True),
            "Ticker": st.column_config.TextColumn(help=tip("ticker")),
            "Empfehlung": st.column_config.TextColumn(help="Stark kaufen ≥ +55 · Kaufen ≥ +25 · Halten · "
                                                          "Verkaufen ≤ −25 · Stark verkaufen ≤ −55"),
            "Score": st.column_config.NumberColumn("Score", format="%+.0f", help=tip("score")),
            "Datum": st.column_config.DateColumn("Verkauf ab / Halten bis", format="DD.MM.YYYY",
                                                 help=tip("zeithorizont")),
            "Kurs": st.column_config.TextColumn(help="Letzter Schlusskurs"),
            "Kursziel": st.column_config.NumberColumn(format="%.2f", help=tip("kursziel")),
            "Potenzial": st.column_config.NumberColumn(format="%+.1f %%", help=tip("potenzial")),
            "Stop-Loss": st.column_config.NumberColumn(format="%.2f", help=tip("stop_loss")),
            "Signalstärke": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f %%",
                                                            help=tip("signalstaerke")),
            "Seit (Tage)": st.column_config.NumberColumn("Aktiv seit (Tage)", help=tip("signal_seit")),
            "Tendenz": st.column_config.TextColumn(help=tip("tendenz")),
        },
    )
    export = recommendations_table(recs).drop(columns=["Label"])
    st.download_button("📥 Tabelle als CSV herunterladen", export.to_csv(index=False, sep=";", decimal=","),
                       file_name="aktien_signale.csv", mime="text/csv")
    if result.errors:
        with st.expander(f"⚠️ {len(result.errors)} Aktien ohne Analyse"):
            for ticker, err in result.errors.items():
                st.write(f"**{ticker}**: {err}")

# --------------------------------------------------------------------------- single stock

with tabs[1]:
    names = {**CATALOG, **{r.ticker: r.name for r in recs}, **st.session_state.get("extra_names", {})}
    options = sorted(names, key=lambda t: names[t].casefold())
    if not st.session_state.get("stock"):
        st.session_state.stock = recs[0].ticker

    picked = st.selectbox(
        "Aktie suchen", options, key="stock", accept_new_options=True,
        format_func=lambda t: f"{names[t]} · {t}" if t in names else t,
        placeholder="Name oder Kürzel eingeben, z. B. Alphabet, Google, SAP oder TSLA",
        help="Durchsucht über 250 Aktien aus DAX, MDAX, Europa, USA und NASDAQ. Nicht dabei? Einfach den Namen "
             "eintippen und mit Enter bestätigen – dann wird bei Yahoo Finance gesucht.")

    ticker = picked
    if picked not in names:  # free text that is not in the catalog
        hits = search_catalog(picked, 1)
        found = [] if hits or source == DEMO else yahoo_search(picked)
        if hits:
            ticker = hits[0][0]
        elif found:
            labels = {f["ticker"]: f"{f['name']} · {f['ticker']} ({f['exchange']})" for f in found}
            ticker = st.radio(f"Suchergebnisse für „{picked}“", list(labels), format_func=labels.get)
            st.session_state.setdefault("extra_names", {})[ticker] = next(f["name"] for f in found
                                                                          if f["ticker"] == ticker)
        else:
            ticker = picked.strip().upper()
    name = {**names, **st.session_state.get("extra_names", {})}.get(ticker, ticker)

    df = result.histories.get(ticker)
    if df is None:
        try:
            df = load_history(source, ticker, period)
        except Exception as exc:
            st.error(f"Kursdaten für {ticker} konnten nicht geladen werden: {exc}")
            df = None

    if df is None or df.empty:
        st.error(f"Keine Kursdaten für „{picked}“ gefunden. Probiere den Firmennamen oder das Kürzel "
                 "(z. B. SAP.DE, GOOGL).")
    else:
        try:
            rec, scores = detailed_analysis(df, ticker, name, result.benchmark)
        except InsufficientDataError as exc:
            st.error(str(exc))
        else:
            pal = palette()
            change = float(df["Close"].iloc[-1] / df["Close"].iloc[-2] - 1) if len(df) > 1 else None
            html(ui.detail_header(rec, change))
            html(ui.section("Was heißt das für dich?"))
            html(ui.action_box(rec))

            html(ui.section("Wichtige Zahlen", "Das ⓘ neben jeder Zahl erklärt den Begriff."))
            m = st.columns(4)
            if rec.side == BUY:
                risk = rec.price - rec.stop_loss
                crv = (rec.target_price - rec.price) / risk if risk > 0 else float("nan")
                m[0].metric("Kursziel", fmt_price(rec.target_price, rec.currency), fmt_pct(rec.expected_return),
                            **CARD, help=tip("kursziel"))
                m[1].metric("Stop-Loss", fmt_price(rec.stop_loss, rec.currency), fmt_pct(rec.stop_loss / rec.price - 1),
                            **CARD, help=tip("stop_loss"))
                m[2].metric("Chance/Risiko", fmt_num(crv, 1), **CARD, help=tip("chance_risiko"))
            elif rec.side == HOLD:
                up = rec.upper_trigger
                low = rec.lower_trigger
                m[0].metric("Kaufsignal über", fmt_price(up, rec.currency),
                            fmt_pct(up / rec.price - 1) if up else None, **CARD, help=tip("preis_schwelle"))
                m[1].metric("Verkaufssignal unter", fmt_price(low, rec.currency),
                            fmt_pct(low / rec.price - 1) if low else None, **CARD, help=tip("preis_schwelle"))
                m[2].metric("Tendenz", rec.tendency.capitalize(), **CARD, help=tip("tendenz"))
            else:
                up = rec.upper_trigger
                m[0].metric("Signal endet über", fmt_price(up, rec.currency),
                            fmt_pct(up / rec.price - 1) if up else None, **CARD, help=tip("preis_schwelle"))
                m[1].metric("Tendenz", rec.tendency.capitalize(), **CARD, help=tip("tendenz"))
                m[2].metric("Signal-Score", fmt_score(rec.score), **CARD, help=tip("score"))
            m[3].metric("Signalstärke", f"{rec.strength * 100:.0f} %", **CARD, help=tip("signalstaerke"))
            m = st.columns(4)
            m[0].metric("Volatilität p. a.", fmt_pct(rec.volatility, 0, sign=False), **CARD,
                        help=tip("volatilitaet"))
            m[1].metric("Tagesschwankung (ATR)", fmt_price(rec.atr, rec.currency),
                        fmt_pct(rec.atr / rec.price, 1, sign=False), delta_arrow="off", delta_color="gray",
                        **CARD, help=tip("atr"))
            m[2].metric("Signal aktiv seit", f"{rec.signal_age} Tagen", **CARD, help=tip("signal_seit"))
            high = df["Close"].iloc[-252:].max()
            m[3].metric("Abstand 52-Wochen-Hoch", fmt_pct(rec.price / high - 1), delta_arrow="off",
                        **CARD, help=tip("hoch_52w"))

            html(ui.section("Kursverlauf und Prognose",
                            "Letzte 12 Monate mit 50- und 200-Tage-Linie, Kursziel, Stop-Loss und Zieldatum"))
            with st.container(border=True):
                st.plotly_chart(charts.price_chart(df, rec, pal), width="stretch", theme="streamlit")

            left, right = st.columns([1, 1], gap="large")
            with left:
                html(ui.section("Warum diese Empfehlung?", "✓ spricht dafür · ! spricht dagegen · – neutral"))
                html(ui.reasons_list(rec.reasons))
            with right:
                html(ui.section("Die sieben Faktoren", "Wie jeder Faktor die Aktie bewertet (−100 bis +100)"))
                with st.container(border=True):
                    st.plotly_chart(charts.component_chart(rec, pal), width="stretch", theme="streamlit")

            html(ui.section("Verlauf des Signal-Scores", "In welcher Zone die Aktie in den letzten 2 Jahren lag"))
            with st.container(border=True):
                st.plotly_chart(charts.score_chart(scores, pal), width="stretch", theme="streamlit")

            with st.expander("📜 Rückblick: Wie gut waren die Signale bei dieser Aktie früher?"):
                st.caption(f"{TERMS['rueckblick'].short} Ohne Gebühren und Steuern.")
                quality = signal_quality(scores, df["Close"])
                strategy = strategy_performance(scores, df["Close"])
                q = quality.rename(index={k: label_text(k) for k in LABELS} | {"ALL": "Alle Tage"})
                q_display = pd.DataFrame({
                    "Tage": q["days"],
                    "Ø Kurs 1 Monat später": [fmt_pct(v) for v in q["mean"]],
                    "Anteil im Plus": [fmt_pct(v, 0, sign=False) for v in q["hit_rate"]],
                }, index=q.index.rename("Signal"))
                left, right = st.columns([2, 3], gap="large")
                with left:
                    st.dataframe(q_display, width="stretch",
                                 column_config={"Anteil im Plus": st.column_config.TextColumn(
                                     help=tip("anteil_im_plus"))})
                    s1, s2 = st.columns(2)
                    s1.metric("Strategie", fmt_pct(strategy.strategy_return), **CARD, help=tip("strategie"))
                    s2.metric("Kaufen & Liegenlassen", fmt_pct(strategy.buy_and_hold_return), **CARD,
                              help=tip("strategie"))
                    s1.metric("Max. Verlust", fmt_pct(strategy.strategy_max_drawdown), **CARD,
                              help=tip("max_verlust"))
                    s2.metric("Max. Verlust", fmt_pct(strategy.buy_and_hold_max_drawdown), **CARD,
                              help=tip("max_verlust"))
                with right:
                    st.plotly_chart(charts.equity_chart(strategy, pal), width="stretch", theme="streamlit")

# --------------------------------------------------------------------------- glossary

with tabs[2]:
    html(ui.section("📖 Lexikon", "Alle Begriffe der App einfach erklärt"))
    search = st.text_input("Begriff suchen", placeholder="🔍 z. B. Volatilität, RSI, Stop-Loss …",
                           label_visibility="collapsed")
    s = search.casefold().strip()
    shown = 0
    for category in CATEGORIES:
        keys = [k for k, t in TERMS.items() if t.category == category
                and (not s or s in (t.title + " " + t.short + " " + t.long).casefold())]
        if not keys:
            continue
        html(ui.section(category))
        html(ui.glossary_grid(keys))
        shown += len(keys)
    if not shown:
        st.info(f"Kein Begriff zu „{search}“ gefunden.")

# --------------------------------------------------------------------------- methodology

with tabs[3]:
    html(ui.section("⚙️ So funktioniert die Analyse"))
    html(ui.steps([
        ("Kurse laden", "Tägliche, dividendenbereinigte Schlusskurse der letzten Jahre von Yahoo Finance – für die "
                        "Aktie und den Vergleichsindex."),
        ("Sieben Faktoren bewerten", "Trend, Momentum, RSI, Abstand zum 52-Wochen-Hoch, Volumen, relative Stärke und "
                                     "Marktumfeld werden je von −100 bis +100 bewertet."),
        ("Score & Einstufung", "Der gewichtete Durchschnitt ergibt den Signal-Score. Die Schwellen ±25 und ±55 "
                               "entscheiden über die fünf Stufen."),
        ("Termine & Kurse", "Verkaufsdatum bzw. Haltedauer, Kursziel, Stop-Loss und Preis-Schwellen werden aus "
                            "Trend, Schwankung und der Historie der Aktie berechnet."),
    ]))
    weights = "\n".join(f"| {COMPONENT_LABELS[k]} | {fmt_num(w * 100, 0)} % |" for k, w in WEIGHTS.items())
    st.markdown(f"""
#### Die fünf Stufen

| Signal-Score | Empfehlung | Was die App zusätzlich sagt |
|---|---|---|
| ab {STRONG_BUY_THRESHOLD:+.0f} | {label_text("STRONG_BUY")} | Verkauf ab Datum, Kursziel, Stop-Loss |
| {BUY_THRESHOLD:+.0f} bis {STRONG_BUY_THRESHOLD:+.0f} | {label_text("BUY")} | Verkauf ab Datum, Kursziel, Stop-Loss |
| {SELL_THRESHOLD:+.0f} bis {BUY_THRESHOLD:+.0f} | {label_text("HOLD")} | Halten bis Datum, Kurse für Kauf-/Verkaufssignal |
| {STRONG_SELL_THRESHOLD:+.0f} bis {SELL_THRESHOLD:+.0f} | {label_text("SELL")} | Neubewertung ab Datum, Kurs für Signalende |
| bis {STRONG_SELL_THRESHOLD:+.0f} | {label_text("STRONG_SELL")} | Neubewertung ab Datum, Kurs für Signalende |

#### Gewichtung der Faktoren

| Faktor | Gewicht |
|---|---|
{weights}

#### Zeithorizont („Verkauf ab“ / „Halten bis“)
Zwei Schätzungen werden gemittelt: (1) wie lange frühere Signale derselben Seite bei dieser Aktie noch anhielten,
nachdem sie so alt waren wie das aktuelle (Median), und (2) der Trend des Scores der letzten 10 Tage, fortgeschrieben
bis zur nächsten Schwelle. Ein Wechsel von „Stark kaufen“ zu „Kaufen“ beendet das Kaufsignal nicht.
Grenzen: Kauf-Seite 2 Wochen bis 9 Monate, Halten/Verkaufen 1 Woche bis 6 Monate.

#### Kursziel und Stop-Loss
- **Stop-Loss** = Kurs − 2 × ATR (durchschnittliche Tagesschwankung).
- **Kursziel** = Aufwärtstrend der letzten 6 Monate, vorsichtig nur zur Hälfte bis zum Verkaufsdatum
  fortgeschrieben (max. 60 % p. a.), mindestens aber Kurs + 3 × ATR (Chance/Risiko ≥ 1,5).

#### Grenzen
- Rein technische Analyse – Nachrichten, Bilanzen und Bewertung (KGV usw.) fließen nicht ein.
- Alle Termine und Kursziele sind **Richtwerte**, keine Prognosen mit Gewähr. **Keine Anlageberatung.**
""")
