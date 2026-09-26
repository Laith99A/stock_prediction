"""Aktien-Kompass: halal stock analysis for beginners (Streamlit app).

Start with:  streamlit run app.py
"""
from __future__ import annotations

import re
import time
from datetime import date

import pandas as pd
import streamlit as st

from stock_analyzer import charts, ui
from stock_analyzer.backtest import signal_quality, strategy_performance
from stock_analyzer.chart_reader import read_chart
from stock_analyzer.chart_school import LESSONS, SHORT
from stock_analyzer.companies import COUNTRY_DE, about
from stock_analyzer.data import SyntheticProvider, YahooProvider, guess_currency, search_yahoo
from stock_analyzer.formatting import fmt_date, fmt_num, fmt_pct, fmt_price, fmt_score, label_text
from stock_analyzer.fundamentals import (
    GROUPS,
    Fundamentals,
    fetch_many,
    rate,
    summarize,
    synthetic_fundamentals,
)
from stock_analyzer.fx import DEMO_RATES, fx_tickers, to_eur
from stock_analyzer.glossary import CATEGORIES, TERMS, tip
from stock_analyzer.halal import CATEGORY, HALAL, MAX_DEBT_TO_EQUITY, NOT_HALAL, HalalCheck, check
from stock_analyzer.learning import quiz, word_of_the_day
from stock_analyzer.market import ScanResult, scan
from stock_analyzer.recommendation import InsufficientDataError, Recommendation, analyze
from stock_analyzer.scoring import (
    BUY,
    BUY_THRESHOLD,
    COMPONENT_LABELS,
    HOLD,
    LABELS,
    SELL_THRESHOLD,
    STRONG_BUY_THRESHOLD,
    STRONG_SELL_THRESHOLD,
    WEIGHTS,
    compute_scores,
)
from stock_analyzer.universes import CATALOG, UNIVERSE_ICON, UNIVERSES, flag, search_catalog

st.set_page_config(page_title="Aktien-Kompass", page_icon="☪️", layout="wide", initial_sidebar_state="expanded")

LIVE = "📡 Live-Kurse (Yahoo Finance)"
DEMO = "🧪 Demo-Daten (offline)"
CUSTOM = "Eigene Liste"
CARD = {"border": True, "height": "stretch"}  # metric tiles as equal-height cards
TAB_DISCOVER, TAB_STOCK, TAB_LEARN, TAB_ABOUT = "🏠 Entdecken", "🔎 Analyse", "🎓 Lernen", "ℹ️ So funktioniert's"
LESSON_TITLES = {lesson.key: f"{i} · {lesson.title}" for i, lesson in enumerate(LESSONS, 1)}
LESSON_KEYS = [lesson.key for lesson in LESSONS]

PRICES = {"Alle": None, "< 20 €": 20, "< 50 €": 50, "< 100 €": 100}
HALAL_MODES = ["☪ Nur halal", "☪ + Prüfen", "Alle"]
RISKS = ["Alle", "🐢 Ruhig", "🚶 Mittel", "🎢 Wild"]
SORTS = ["🔥 Beste Chancen", "💶 Günstigster Preis", "🧮 Niedrigstes KGV", "💰 Höchste Dividende", "🐢 Ruhigste zuerst",
         "🔤 Name A–Z"]
SECTOR_DE = {
    "Technology": "Technologie", "Healthcare": "Gesundheit", "Consumer Cyclical": "Konsum (zyklisch)",
    "Consumer Defensive": "Basiskonsum", "Industrials": "Industrie", "Energy": "Energie",
    "Basic Materials": "Rohstoffe", "Communication Services": "Kommunikation", "Utilities": "Versorger",
    "Real Estate": "Immobilien", "Financial Services": "Finanzen",
}

# Default value of every setting and filter. Widgets get their default passed directly and keep their value
# with persist_state="session", so filters survive while they are hidden (e.g. during loading errors).
DEFAULTS = {
    "market": "Beliebt", "source": LIVE, "period": "5y", "view": "Karten",
    "custom": "Apple, Microsoft, Alphabet, NVIDIA, SAP, ASML, Tencent, BYD, Novo Nordisk",
    "f_query": "", "f_price": "Alle", "f_halal": HALAL_MODES[0], "f_risk": "Alle", "f_sort": SORTS[0],
    "f_labels": [label_text(k) for k in LABELS], "f_sectors": [], "f_dividend": False,
}
KEEP = {"persist_state": "session"}
st.session_state.setdefault("page_size", 12)
st.session_state.setdefault("market", DEFAULTS["market"])  # set by the sidebar buttons


def state(key: str):
    """Current value of a setting or filter (its default before the widget exists)."""
    return st.session_state.get(key, DEFAULTS[key])


# --------------------------------------------------------------------------- data

def provider_for(source: str):
    return SyntheticProvider() if source == DEMO else YahooProvider()


@st.cache_data(ttl=3600, show_spinner="Kurse werden geladen und analysiert …")
def run_scan(source: str, tickers: tuple[tuple[str, str], ...], benchmark: str, benchmark_name: str,
             period: str) -> ScanResult:
    return scan(provider_for(source), dict(tickers), benchmark or None, benchmark_name, period=period)


@st.cache_data(ttl=3600, show_spinner="Kurse werden geladen …")
def load_history(source: str, ticker: str, period: str) -> pd.DataFrame | None:
    return provider_for(source).history([ticker], period=period).get(ticker)


@st.cache_data(ttl=3600, show_spinner="Analyse wird berechnet …")
def detailed_analysis(df: pd.DataFrame, ticker: str, name: str, benchmark: pd.Series | None):
    scores = compute_scores(df, benchmark)
    rec = analyze(df, ticker, name=name, currency=guess_currency(ticker), benchmark=benchmark,
                  with_triggers=True, scores=scores)
    return rec, scores


@st.cache_resource
def _fundamentals_store() -> dict[str, tuple[float, Fundamentals]]:
    """Key figures shared across reruns and markets (ticker -> (expires_at, data))."""
    return {}


def load_fundamentals(source: str, items: tuple[tuple[str, float], ...]) -> dict[str, Fundamentals]:
    if source == DEMO:
        return {t: synthetic_fundamentals(t, p) for t, p in items}
    store, now = _fundamentals_store(), time.time()
    missing = [t for t, _ in items if t not in store or store[t][0] < now]
    if missing:
        with st.spinner(f"Kennzahlen für {len(missing)} Aktien werden geladen (einmalig, bis zu einer Minute) …"):
            for ticker, data in fetch_many(missing, workers=6).items():
                # Keep good data for 12 hours; retry failed lookups after 10 minutes.
                store[ticker] = (now + (12 * 3600 if data.available else 600), data)
    return {t: store[t][1] for t, _ in items if t in store}


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def load_fx(source: str, currencies: tuple[str, ...]) -> dict[str, float]:
    if source == DEMO:
        return DEMO_RATES
    symbols = fx_tickers(set(currencies))
    try:
        history = YahooProvider().history(list(symbols.values()), period="1mo")
    except Exception:
        return {}
    return {code: float(history[sym]["Close"].iloc[-1]) for code, sym in symbols.items() if sym in history}


@st.cache_data(ttl=24 * 3600, show_spinner="Suche bei Yahoo Finance …")
def yahoo_search(query: str) -> list[dict[str, str]]:
    return search_yahoo(query)


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


def risk_of(volatility: float) -> str:
    if volatility < 0.25:
        return RISKS[1]
    if volatility < 0.45:
        return RISKS[2]
    return RISKS[3]


def html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def how_to(lines: list[str]) -> None:
    """Expander that explains how to read the chart above it."""
    with st.expander("📖 Wie lese ich diesen Chart?"):
        st.markdown("\n".join(f"- {line}" for line in lines))


def open_stock(ticker: str) -> None:
    """Callback: show a stock in the analysis tab."""
    st.session_state.stock = ticker
    st.session_state.nav = TAB_STOCK


# --------------------------------------------------------------------------- load the selected market

html(ui.css())
def select_market(name: str) -> None:
    st.session_state.market = name
    st.session_state.page_size = 12


def render_sidebar() -> None:
    """Narrow sidebar: market navigation and settings."""
    with st.sidebar:
        html('<div class="brand">☪️ Aktien-Kompass</div><div class="brand-sub">Halal investieren. Einfach verstehen.</div>')
        html('<div class="navlabel">Markt</div>')
        for name in [*UNIVERSES, CUSTOM]:
            count = f" · {len(UNIVERSES[name]['tickers'])}" if name in UNIVERSES else ""
            st.button(f"{UNIVERSE_ICON.get(name, '⭐')} {name}{count}", key=f"market-{name}", width="stretch",
                      type="primary" if st.session_state.market == name else "tertiary",
                      on_click=select_market, args=(name,))
        if st.session_state.market == CUSTOM:
            st.text_area("Deine Aktien", key="custom", value=DEFAULTS["custom"], height=110, **KEEP,
                         help="Namen oder Kürzel mit Komma getrennt, z. B. „Alphabet, SAP, Tencent“ oder GOOGL, "
                              "SAP.DE, 0700.HK.")
        html('<div class="navlabel" style="margin-top:14px">Einstellungen</div>')
        with st.expander("⚙️ Daten & Historie"):
            st.radio("Datenquelle", [LIVE, DEMO], key="source", **KEEP,
                     help="Live-Kurse kommen von Yahoo Finance. Demo-Daten sind simulierte Kurse zum Ausprobieren.")
            st.select_slider("Historie", ["2y", "5y", "10y"], key="period", value=DEFAULTS["period"], **KEEP,
                             format_func=lambda p: p.replace("y", " Jahre"),
                             help="Mehr Historie = bessere Schätzung der Signaldauer, aber langsameres Laden.")
            if st.button("🔄 Daten neu laden", width="stretch"):
                st.cache_data.clear()
                _fundamentals_store().clear()
                st.rerun()
        st.caption("⚠️ Keine Anlageberatung. Alle Angaben sind Richtwerte.")


render_sidebar()
source = state("source")
market = st.session_state.market
if market == CUSTOM:
    tickers = resolve_entries(state("custom"), live=source == LIVE)
    benchmark, benchmark_name = "URTH", "MSCI World"
else:
    universe = UNIVERSES[market]
    tickers, benchmark, benchmark_name = universe["tickers"], universe["benchmark"], universe["benchmark_name"]

html(ui.hero(
    "☪️ Aktien-Kompass",
    "Halal investieren.<br><span>Einfach verstehen.</span>",
    "Halal-konforme Aktien aus den USA, Europa und China – mit klarer Empfehlung, Kennzahlen und einer Erklärung "
    "für jeden Begriff. Fahre über unterstrichene Wörter oder ⓘ, um sie zu verstehen.",
    ["🧪 Demo-Daten" if source == DEMO else "📡 Live-Kurse", f"🌍 {len(CATALOG)} Aktien", "⚠️ Keine Anlageberatung"],
))

result: ScanResult | None = None
load_error = ""
if tickers:
    try:
        result = run_scan(source, tuple(tickers.items()), benchmark, benchmark_name, state("period"))
    except Exception as exc:  # network / rate limit problems from yfinance
        load_error = str(exc)
recs: list[Recommendation] = result.recommendations if result else []

funda: dict[str, Fundamentals] = {}
rates: dict[str, float] = {}
checks: dict[str, HalalCheck] = {}
if recs:
    funda = load_fundamentals(source, tuple((r.ticker, r.price) for r in recs))
    rates = load_fx(source, tuple(sorted({r.currency for r in recs})))
    checks = {r.ticker: check(r.ticker, funda.get(r.ticker)) for r in recs}

tabs = st.tabs([TAB_DISCOVER, TAB_STOCK, TAB_LEARN, TAB_ABOUT], key="nav", on_change="rerun")


# --------------------------------------------------------------------------- discover

def build_table() -> pd.DataFrame:
    rows = []
    for r in recs:
        f = funda.get(r.ticker) or Fundamentals(r.ticker)
        df = result.histories.get(r.ticker)
        change = float(df["Close"].iloc[-1] / df["Close"].iloc[-2] - 1) if df is not None and len(df) > 1 else None
        c = checks[r.ticker]
        rows.append({
            "ticker": r.ticker, "name": r.name, "flag": flag(r.ticker), "label": r.label, "side": r.side,
            "empfehlung": r.label_text, "score": r.score, "datum": r.horizon_date, "price": r.price,
            "currency": r.currency, "price_eur": to_eur(r.price, r.currency, rates), "change": change,
            "sector": "" if f.is_demo else SECTOR_DE.get(f.sector or "", f.sector or ""),
            "pe": f.pe, "pb": f.pb, "de": f.debt_to_equity,
            "dividend": f.dividend_yield, "volatility": r.volatility, "risk": risk_of(r.volatility),
            "halal": c.status, "halal_text": f"{c.icon} {c.label}", "halal_reason": " · ".join(c.reasons),
        })
    return pd.DataFrame(rows)


def apply_filters(table: pd.DataFrame) -> pd.DataFrame:
    mask = table["empfehlung"].isin(state("f_labels") or [])
    if state("f_halal") == HALAL_MODES[0]:
        mask &= table["halal"] == HALAL
    elif state("f_halal") == HALAL_MODES[1]:
        mask &= table["halal"] != NOT_HALAL
    limit = PRICES.get(state("f_price"))
    if limit:
        price = table["price_eur"].fillna(table["price"])
        mask &= price < limit
    if state("f_risk") not in (None, "Alle"):
        mask &= table["risk"] == state("f_risk")
    if state("f_sectors"):
        mask &= table["sector"].isin(state("f_sectors"))
    if state("f_dividend"):
        mask &= table["dividend"].fillna(0) > 0
    query = (state("f_query") or "").strip().casefold()
    if query:
        mask &= (table["name"].str.casefold().str.contains(query, regex=False)
                 | table["ticker"].str.casefold().str.contains(query, regex=False))
    out = table[mask]
    by = {
        SORTS[0]: ("score", False), SORTS[1]: ("price_eur", True), SORTS[2]: ("pe", True),
        SORTS[3]: ("dividend", False), SORTS[4]: ("volatility", True), SORTS[5]: ("name", True),
    }[state("f_sort") or SORTS[0]]
    return out.sort_values(by[0], ascending=by[1], na_position="last").reset_index(drop=True)


def show_more() -> None:
    st.session_state.page_size += 12


def on_table_select() -> None:
    rows = st.session_state.stock_table.selection.rows
    if rows:
        open_stock(st.session_state.table_tickers[rows[0]])


def render_discover() -> None:
    title = "Eigene Liste" if market == CUSTOM else f"{UNIVERSE_ICON.get(market, '')} {market}"
    html(ui.section(title, f"{len(tickers)} Aktien in dieser Auswahl"))
    if market == "China":
        st.caption("🇨🇳 Chinesische Aktien werden mit den Kursen der Heimatbörse Hongkong analysiert. In Europa "
                   "kannst du sie in Euro über deutsche Börsen handeln (z. B. Tradegate, Frankfurt, Neobroker).")
    if source == DEMO:
        st.caption("🧪 Demo-Modus: Kurse und Kennzahlen sind simuliert und haben nichts mit den echten Aktien zu tun.")

    if not recs:
        if load_error:
            st.error(f"Kursdaten konnten nicht geladen werden: {load_error}")
        else:
            st.error("Für diese Auswahl konnten keine Kursdaten geladen werden.")
        st.info("Tipp: Internetverbindung prüfen oder links unter ⚙️ „Demo-Daten (offline)“ wählen.")
        return

    table = build_table()
    n_halal = int((table["halal"] == HALAL).sum())
    n_buy = int(((table["halal"] == HALAL) & (table["side"] == BUY)).sum())
    secondary = []
    if result.regime is not None:
        regime = result.regime
        secondary.append((f"{ui.term('Markttrend', 'marktumfeld')} · {regime.name}", regime.short_label,
                          f"{fmt_pct(regime.perf_1m)} im letzten Monat"))
    secondary.append((f"☪️ {ui.term('Halal-konform', 'halal_investieren')}", f"{n_halal} von {len(table)}",
                      "bestehen Geschäftsfeld- und Schulden-Check"))
    primary = ("🟢 Halal + Kaufsignal", str(n_buy), "Aktien mit „Kaufen“ oder „Stark kaufen“ in dieser Auswahl")
    html(ui.pulse(primary, secondary, extra=ui.word_card(word_of_the_day())))

    # ---- filter bar
    f1, f2, f3 = st.columns([2.2, 1.6, 1.6])
    f1.text_input("🔍 Suche", key="f_query", placeholder="Name oder Kürzel, z. B. Tesla", **KEEP)
    f2.segmented_control("💶 Preis pro Aktie", list(PRICES), key="f_price", default=DEFAULTS["f_price"], required=True,
                         width="stretch", **KEEP,
                         help="Preis einer einzelnen Aktie in Euro (umgerechnet). Achtung: Ein niedriger Preis heißt "
                              "nicht, dass die Aktie günstig bewertet ist – das zeigt das KGV. Bei vielen Brokern "
                              "kannst du auch Bruchstücke teurer Aktien kaufen.")
    f3.segmented_control("☪️ Halal-Filter", HALAL_MODES, key="f_halal", default=DEFAULTS["f_halal"], required=True,
                         width="stretch", **KEEP,
                         help="Nur halal: Geschäftsfeld erlaubt und Debt-to-Equity ≤ 0,33. „+ Prüfen“ zeigt "
                              "zusätzlich Grenzfälle und Aktien ohne Schulden-Daten.")
    g1, g2 = st.columns([3.2, 1.8], vertical_alignment="bottom")
    g1.pills("🎯 Empfehlung", [label_text(k) for k in LABELS], key="f_labels", selection_mode="multi",
             default=DEFAULTS["f_labels"], help=tip("score"), **KEEP)
    g2.segmented_control("🎢 Risiko", RISKS, key="f_risk", default=DEFAULTS["f_risk"], required=True, width="stretch",
                         **KEEP,
                         help="Nach Schwankung pro Jahr: ruhig unter 25 %, mittel 25–45 %, wild über 45 %. "
                              + tip("volatilitaet"))

    shown = apply_filters(table)
    h1, h2, h3, h4 = st.columns([2.4, 1.3, 0.9, 1.3], vertical_alignment="center")
    h1.markdown(f"**{len(shown)} Aktien** passen zu deinen Filtern")
    h2.selectbox("Sortieren", SORTS, key="f_sort", label_visibility="collapsed", **KEEP)
    with h3.popover("➕ Mehr", width="stretch"):
        st.multiselect("Branche", sorted(SECTOR_DE.values()), key="f_sectors", placeholder="Alle Branchen", **KEEP,
                       help="Im Demo-Modus gibt es keine Branchen-Daten.")
        st.toggle("💰 Nur Aktien mit Dividende", key="f_dividend", help=tip("dividendenrendite"), **KEEP)
    h4.segmented_control("Ansicht", ["Karten", "Tabelle"], key="view", default=DEFAULTS["view"], required=True,
                         width="stretch", label_visibility="collapsed", **KEEP,
                         format_func={"Karten": "🃏 Karten", "Tabelle": "📋 Tabelle"}.get)

    if shown.empty:
        st.info("Keine Aktie passt zu deinen Filtern. Tipp: Wähle einen anderen Markt, einen höheren Preis oder "
                "„☪ + Prüfen“.")
    elif state("view") == "Karten":
        by_ticker = {r.ticker: r for r in recs}
        visible = shown.head(st.session_state.page_size)
        for start in range(0, len(visible), 3):
            cols = st.columns(3)
            for col, (_, row) in zip(cols, visible.iloc[start:start + 3].iterrows()):
                rec = by_ticker[row["ticker"]]
                with col:
                    description, _ = about(rec.ticker, (funda.get(rec.ticker) or Fundamentals(rec.ticker)).summary,
                                           max_chars=140)
                    html(ui.stock_tile(rec, checks[rec.ticker], row["flag"], row["price_eur"], row["change"],
                                       row["sector"], result.histories[rec.ticker]["Close"], description))
                    st.button("Analysieren →", key=f"open-{rec.ticker}", on_click=open_stock, args=(rec.ticker,),
                              width="stretch")
        if len(shown) > len(visible):
            st.button(f"Mehr anzeigen ({len(shown) - len(visible)} weitere)", on_click=show_more, width="stretch")
    else:
        st.session_state.table_tickers = list(shown["ticker"])
        view = shown.copy()
        view["aktie"] = view["flag"] + " " + view["name"]
        view["kurs"] = [fmt_price(p, c) for p, c in zip(view["price"], view["currency"])]
        view["score"] = view["score"].astype(int)  # truncated like fmt_score, so it matches the category
        view["datum"] = pd.to_datetime(view["datum"]).dt.date
        view["dividend"] = view["dividend"] * 100
        st.dataframe(
            view, hide_index=True, width="stretch", height=min(40 + 35 * len(view), 700), placeholder="–",
            key="stock_table", on_select=on_table_select, selection_mode="single-row",
            column_order=["aktie", "ticker", "halal_text", "empfehlung", "score", "datum", "price_eur", "kurs",
                          "pe", "pb", "de", "dividend", "risk", "sector"],
            column_config={
                "aktie": st.column_config.TextColumn("Aktie", pinned=True),
                "ticker": st.column_config.TextColumn("Kürzel", help=tip("ticker")),
                "halal_text": st.column_config.TextColumn("Halal", help=tip("halal_investieren")),
                "empfehlung": st.column_config.TextColumn("Empfehlung", help=tip("score")),
                "score": st.column_config.NumberColumn("Score", format="%+d", help=tip("score")),
                "datum": st.column_config.DateColumn("Verkauf ab / Halten bis", format="DD.MM.YYYY",
                                                     help=tip("zeithorizont")),
                "price_eur": st.column_config.NumberColumn("Preis €", format="%.2f €",
                                                           help="Preis pro Aktie in Euro (umgerechnet)"),
                "kurs": st.column_config.TextColumn("Kurs (Börse)", help="Kurs in der Währung der Heimatbörse"),
                "pe": st.column_config.NumberColumn("KGV", format="%.1f", help=tip("kgv")),
                "pb": st.column_config.NumberColumn("KBV", format="%.2f", help=tip("kbv")),
                "de": st.column_config.NumberColumn("Debt/Equity", format="%.2f", help=tip("verschuldungsgrad")),
                "dividend": st.column_config.NumberColumn("Dividende", format="%.1f %%", help=tip("dividendenrendite")),
                "risk": st.column_config.TextColumn("Risiko", help=tip("volatilitaet")),
                "sector": st.column_config.TextColumn("Branche"),
            },
        )
        export = shown.drop(columns=["label", "side", "halal"])
        st.download_button("📥 Als CSV herunterladen", export.to_csv(index=False, sep=";", decimal=","),
                           file_name="aktien_kompass.csv", mime="text/csv")
    if result.errors:
        with st.expander(f"⚠️ {len(result.errors)} Aktien ohne Kursdaten"):
            for ticker, err in result.errors.items():
                st.write(f"**{ticker}**: {err}")


with tabs[0]:
    render_discover()


# --------------------------------------------------------------------------- single stock

def render_stock() -> None:
    names = {**CATALOG, **{r.ticker: r.name for r in recs}, **st.session_state.get("extra_names", {})}
    options = sorted(names, key=lambda t: names[t].casefold())
    if not st.session_state.get("stock"):
        st.session_state.stock = recs[0].ticker if recs else "AAPL"

    picked = st.selectbox(
        "Aktie suchen", options, key="stock", accept_new_options=True,
        format_func=lambda t: f"{flag(t)} {names[t]} · {t}" if t in names else t,
        placeholder="Name oder Kürzel eingeben, z. B. Alphabet, Tencent, SAP",
        help=f"Durchsucht {len(CATALOG)} Aktien aus den USA, Europa und China. Nicht dabei? Namen eintippen und "
             "mit Enter bestätigen – dann wird bei Yahoo Finance gesucht.")

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

    df = result.histories.get(ticker) if result else None
    if df is None:
        try:
            df = load_history(source, ticker, state("period"))
        except Exception as exc:
            st.error(f"Kursdaten für {ticker} konnten nicht geladen werden: {exc}")
            df = None
    if df is None or df.empty:
        st.error(f"Keine Kursdaten für „{picked}“ gefunden. Probiere den Firmennamen oder das Kürzel "
                 "(z. B. SAP.DE, GOOGL, 0700.HK).")
        return
    try:
        rec, scores = detailed_analysis(df, ticker, name, result.benchmark if result else None)
    except InsufficientDataError as exc:
        st.error(str(exc))
        return

    pal = charts.PALETTES["dark"]
    f = load_fundamentals(source, ((ticker, rec.price),)).get(ticker) or Fundamentals(ticker)
    halal = check(ticker, f)
    fx = rates or load_fx(source, (rec.currency,))
    price_eur = to_eur(rec.price, rec.currency, fx)
    change = float(df["Close"].iloc[-1] / df["Close"].iloc[-2] - 1) if len(df) > 1 else None
    html(ui.detail_header(rec, change, halal, flag(ticker), price_eur))
    if halal.status == NOT_HALAL:
        st.warning(f"Diese Aktie ist **nicht halal-konform** ({' · '.join(halal.reasons)}). Die Analyse siehst du "
                   "trotzdem – zum Lernen.", icon="☪️")

    sub = st.tabs(["🧾 Überblick", "📊 Kennzahlen", "🧭 Chart-Leser", "🔬 Hintergrund"])
    with sub[0]:
        description, german = about(ticker, f.summary)
        location = ", ".join(x for x in (f.city, COUNTRY_DE.get(f.country or "", f.country)) if x)
        sector = " · ".join(x for x in (SECTOR_DE.get(f.sector or "", f.sector), f.industry) if x and not f.is_demo)
        trading = "Heimatbörse Hongkong · in Europa handelbar" if flag(ticker) == "🇨🇳" and ticker.endswith(".HK") \
            else ""
        facts = [
            ("Branche", sector),
            ("Sitz", location),
            ("Mitarbeiter", fmt_num(f.employees, 0) if f.employees else ""),
            ("Börsenwert", f"{ui.big_number(f.market_cap)} {'GBP' if rec.currency == 'GBp' else rec.currency}"
             if f.market_cap else ""),
            ("Kürzel", ticker),
            ("Handel", trading),
        ]
        html(ui.company_card(name, description, german, facts, f.website))
        if german and f.summary:
            with st.expander("Ausführliche Beschreibung (Englisch, Yahoo Finance)"):
                st.write(f.summary)

        left, right = st.columns([2, 3], gap="large")
        with left:
            html(ui.section("☪️ Halal-Check"))
            html(ui.halal_card(halal))
        with right:
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
            up, low = rec.upper_trigger, rec.lower_trigger
            m[0].metric("Kaufsignal über", fmt_price(up, rec.currency), fmt_pct(up / rec.price - 1) if up else None,
                        **CARD, help=tip("preis_schwelle"))
            m[1].metric("Verkaufssignal unter", fmt_price(low, rec.currency),
                        fmt_pct(low / rec.price - 1) if low else None, **CARD, help=tip("preis_schwelle"))
            m[2].metric("Tendenz", rec.tendency.capitalize(), **CARD, help=tip("tendenz"))
        else:
            up = rec.upper_trigger
            m[0].metric("Signal endet über", fmt_price(up, rec.currency), fmt_pct(up / rec.price - 1) if up else None,
                        **CARD, help=tip("preis_schwelle"))
            m[1].metric("Tendenz", rec.tendency.capitalize(), **CARD, help=tip("tendenz"))
            m[2].metric("Signal-Score", fmt_score(rec.score), **CARD, help=tip("score"))
        m[3].metric("Signalstärke", f"{rec.strength * 100:.0f} %", **CARD, help=tip("signalstaerke"))
        m = st.columns(4)
        m[0].metric("Volatilität p. a.", fmt_pct(rec.volatility, 0, sign=False), risk_of(rec.volatility),
                    delta_arrow="off", delta_color="gray", **CARD, help=tip("volatilitaet"))
        m[1].metric("Debt-to-Equity", fmt_num(f.debt_to_equity, 2) if f.debt_to_equity is not None else "–",
                    "halal ≤ 0,33", delta_arrow="off", delta_color="gray", **CARD, help=tip("verschuldungsgrad"))
        m[2].metric("KGV", fmt_num(f.pe, 1) if f.pe is not None else "–", **CARD, help=tip("kgv"))
        m[3].metric("Signal aktiv seit", f"{rec.signal_age} Tagen", **CARD, help=tip("signal_seit"))

        html(ui.section("Kursverlauf und Prognose",
                        "Letzte 12 Monate mit 50- und 200-Tage-Linie, Kursziel, Stop-Loss und Zieldatum"))
        with st.container(border=True):
            st.plotly_chart(charts.price_chart(df, rec, pal), width="stretch", theme="streamlit")
        how_to([
            "**Blaue Linie** = Kurs (Schlusskurs je Handelstag), **orange** = 50-Tage-Linie, **grün** = 200-Tage-Linie.",
            "Liegt Blau über Grün, ist der langfristige Trend intakt. Kreuzt Orange die grüne Linie nach oben, ist "
            "das ein **Golden Cross** (bullish), nach unten ein **Death Cross** (bearish).",
            "**Grün gestrichelt** = Kursziel, **rot gestrichelt** = Stop-Loss, **grau gepunktet** = Kurse, ab denen "
            "sich die Empfehlung ändern würde.",
            "Die **senkrechte gepunktete Linie** markiert das Datum „Verkauf ab“ bzw. „Halten bis“.",
            "Mehr dazu unter **🎓 Lernen → Chart-Schule**.",
        ])

    with sub[1]:
        metrics = rate(f)
        html(ui.section("📊 Kennzahlen des Unternehmens",
                        f"{ui.term('Fundamentaldaten', 'fundamentalanalyse')} ergänzen die Chart-Analyse: Wie teuer "
                        "ist die Aktie, wie hoch verschuldet, wie profitabel?"))
        if not f.available:
            st.info("Für dieses Wertpapier liefert Yahoo Finance keine Kennzahlen (z. B. bei ETFs) – oder die "
                    "Verbindung ist gerade gestört.")
        else:
            meta = " · ".join(x for x in (SECTOR_DE.get(f.sector or "", f.sector), f.industry) if x)
            note = "🧪 Demo-Kennzahlen (simuliert)" if f.is_demo else "Quelle: Yahoo Finance, letzte 12 Monate"
            st.caption(f"{meta + ' · ' if meta else ''}{note}. Die Ampeln folgen allgemeinen Faustregeln – was "
                       "„teuer“ ist, hängt auch von der Branche ab.")
            html(ui.fundamentals_summary(summarize(metrics)))
            for group in GROUPS:
                group_metrics = [x for x in metrics if x.group == group]
                if group_metrics:
                    html(ui.section(group))
                    html(ui.metric_grid(group_metrics))

    with sub[2]:
        reading = read_chart(df)
        html(ui.section("🧭 Was zeigt der Chart gerade?",
                        "Die App liest den Chart wie ein Chartanalyst und zählt die Zeichen für steigende (bullish) "
                        "und fallende (bearish) Kurse."))
        html(ui.reading_summary(reading))
        left, right = st.columns([3, 2], gap="large")
        with left:
            with st.container(border=True):
                st.plotly_chart(charts.reading_chart(df, reading, pal), width="stretch", theme="streamlit")
            how_to([
                "Die **nummerierten Punkte** gehören zu den Zeichen in der Liste: **grün** spricht für steigende, "
                "**rot** für fallende Kurse.",
                "**Grün gepunktet** = nächste Unterstützung (Boden), **rot gepunktet** = nächster Widerstand (Decke).",
                "Zeichen ohne Punkt (z. B. RSI oder Volumen) beziehen sich auf die letzten Tage.",
            ])
        with right:
            html(ui.reading_list(reading, LESSON_TITLES))
        st.warning("Kein Zeichen ist sicher. Je mehr Zeichen in dieselbe Richtung zeigen, desto wahrscheinlicher – "
                   "aber nie garantiert – setzt sich die Bewegung fort.", icon="⚠️")
        html(ui.section("Volumen, RSI & MACD", "Die Werkzeuge aus der Chart-Schule für diese Aktie"))
        with st.container(border=True):
            st.plotly_chart(charts.indicator_chart(df, pal), width="stretch", theme="streamlit")
        how_to([
            "**Volumen:** hohe grüne Balken = viel Handel an Gewinntagen (Käufer aktiv), hohe rote Balken = "
            "Verkaufsdruck.",
            "**RSI:** Linie im rötlichen Bereich über 70 = überkauft, im grünlichen Bereich unter 30 = überverkauft.",
            "**MACD:** Kreuzt die blaue Linie die orange nach oben, nimmt der Schwung zu; nach unten lässt er nach.",
        ])

    with sub[3]:
        left, right = st.columns([1, 1], gap="large")
        with left:
            html(ui.section("Warum diese Empfehlung?", "✓ spricht dafür · ! spricht dagegen · – neutral"))
            html(ui.reasons_list(rec.reasons))
        with right:
            html(ui.section("Die sieben Faktoren", "Wie jeder Faktor die Aktie bewertet (−100 bis +100)"))
            with st.container(border=True):
                st.plotly_chart(charts.component_chart(rec, pal), width="stretch", theme="streamlit")
            how_to([
                "Jeder Balken ist ein Faktor. **Nach rechts (blau)** spricht er für die Aktie, **nach links (rot)** "
                "dagegen.",
                "Je länger der Balken, desto stärker. Trend und Momentum zählen am meisten (je 25 %).",
            ])
        html(ui.section("Verlauf des Signal-Scores", "In welcher Zone die Aktie in den letzten 2 Jahren lag"))
        with st.container(border=True):
            st.plotly_chart(charts.score_chart(scores, pal), width="stretch", theme="streamlit")
        how_to([
            "Die Linie ist der **Signal-Score**, die Gesamtnote. Die farbigen Zonen entsprechen den fünf Empfehlungen.",
            "Wechselt die Linie in eine andere Zone, ändert sich die Empfehlung.",
        ])
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
                             column_config={"Anteil im Plus": st.column_config.TextColumn(help=tip("anteil_im_plus"))})
                s1, s2 = st.columns(2)
                s1.metric("Strategie", fmt_pct(strategy.strategy_return), **CARD, help=tip("strategie"))
                s2.metric("Kaufen & Liegenlassen", fmt_pct(strategy.buy_and_hold_return), **CARD,
                          help=tip("strategie"))
                s1.metric("Max. Verlust", fmt_pct(strategy.strategy_max_drawdown), **CARD, help=tip("max_verlust"))
                s2.metric("Max. Verlust", fmt_pct(strategy.buy_and_hold_max_drawdown), **CARD,
                          help=tip("max_verlust"))
            with right:
                st.plotly_chart(charts.equity_chart(strategy, pal), width="stretch", theme="streamlit")


with tabs[1]:
    render_stock()


# --------------------------------------------------------------------------- learn

def step_lesson(delta: int) -> None:
    position = LESSON_KEYS.index(st.session_state.lesson)
    st.session_state.lesson = LESSON_KEYS[(position + delta) % len(LESSON_KEYS)]


def render_school() -> None:
    st.info("Charts zeigen **Wahrscheinlichkeiten, keine Gewissheiten**. Kein einzelnes Zeichen ist sicher – achte "
            "darauf, ob mehrere Zeichen in dieselbe Richtung zeigen, und sichere dich mit einem Stop-Loss ab.",
            icon="💡")
    if st.session_state.get("lesson") not in LESSON_KEYS:
        st.session_state.lesson = LESSON_KEYS[0]
    st.segmented_control("Lektion", LESSON_KEYS, key="lesson", required=True, label_visibility="collapsed",
                         width="stretch", format_func=lambda k: f"{LESSON_KEYS.index(k) + 1} · {SHORT[k]}")
    lesson = LESSONS[LESSON_KEYS.index(st.session_state.lesson)]
    html(ui.section(f"{lesson.icon} Lektion {LESSON_KEYS.index(lesson.key) + 1}: {lesson.title}"))
    chart = charts.lesson_chart(lesson.key, charts.PALETTES["dark"])
    if chart is None:
        html(ui.lesson_card(lesson))
    else:
        left, right = st.columns([2, 3], gap="large")
        with left:
            html(ui.lesson_card(lesson))
        with right:
            with st.container(border=True):
                st.plotly_chart(chart, width="stretch", theme="streamlit")
            st.caption("Beispiel-Chart zur Veranschaulichung (keine echte Aktie).")
    b1, b2, _ = st.columns([1, 1, 4])
    b1.button("← Zurück", on_click=step_lesson, args=(-1,), width="stretch")
    b2.button("Weiter →", on_click=step_lesson, args=(1,), width="stretch", type="primary")
    html(ui.section("✅ Checkliste: Woran erkenne ich, wohin es geht?",
                    "Je mehr Punkte einer Spalte zutreffen, desto klarer das Bild. Der „🧭 Chart-Leser“ bei jeder Aktie "
                    "prüft diese Punkte automatisch."))
    html(ui.checklist())


def render_glossary() -> None:
    search = st.text_input("Begriff suchen", placeholder="🔍 z. B. Bullish, KGV, Debt-to-Equity, Riba …",
                           label_visibility="collapsed")
    s = search.casefold().strip()
    shown = 0
    for category in CATEGORIES:
        term_keys = [k for k, t in TERMS.items() if t.category == category
                     and (not s or s in (t.title + " " + t.short + " " + t.long).casefold())]
        if not term_keys:
            continue
        html(ui.section(category))
        html(ui.glossary_grid(term_keys))
        shown += len(term_keys)
    if not shown:
        st.info(f"Kein Begriff zu „{search}“ gefunden.")


def check_quiz() -> None:
    st.session_state.quiz_checked = st.session_state.quiz_seed


def new_quiz() -> None:
    st.session_state.quiz_seed += 1


def render_quiz() -> None:
    st.session_state.setdefault("quiz_seed", date.today().toordinal())
    seed = st.session_state.quiz_seed
    questions = quiz(seed)
    st.caption("5 Fragen zur Sprache der Investoren. Wähle jeweils die richtige Erklärung.")
    for i, q in enumerate(questions):
        st.radio(f"**{i + 1}. {q.prompt}**", q.options, index=None, key=f"quiz-{seed}-{i}")
    b1, b2, _ = st.columns([1, 1, 3])
    b1.button("✅ Auswerten", on_click=check_quiz, type="primary", width="stretch")
    b2.button("🔄 Neue Fragen", on_click=new_quiz, width="stretch")
    if st.session_state.get("quiz_checked") == seed:
        correct = 0
        for i, q in enumerate(questions):
            right = st.session_state.get(f"quiz-{seed}-{i}") == q.options[q.answer]
            correct += right
            st.markdown(f"{'✅' if right else '❌'} **{TERMS[q.key].title}:** {TERMS[q.key].short}")
        verdict = {5: "Perfekt – du sprichst Investor! 🏆", 4: "Stark! 💪", 3: "Gut – weiter so! 📈"}.get(
            correct, "Übung macht den Meister – schau ins Lexikon. 📖")
        st.success(f"**{correct} von {len(questions)} richtig.** {verdict}")


with tabs[2]:
    learn = st.tabs(["📚 Chart-Schule", "📖 Lexikon", "🧠 Quiz"])
    with learn[0]:
        render_school()
    with learn[1]:
        render_glossary()
    with learn[2]:
        render_quiz()


# --------------------------------------------------------------------------- about

with tabs[3]:
    excluded = ", ".join(v.split(" ", 1)[1] for k, v in CATEGORY.items() if k not in ("unterhaltung", "hotel", "krypto"))
    html(ui.section("☪️ So prüft die App auf Halal"))
    html(ui.steps([
        ("Geschäftsfeld", f"Ausgeschlossen: {excluded}."),
        ("Grenzfälle", "Musik-/Filmunterhaltung, Krypto, kleine Rüstungsanteile oder Hotels mit Alkohol bewerten "
                       "Gelehrte unterschiedlich – sie stehen auf „❔ Prüfen“."),
        ("Schulden", f"Debt-to-Equity höchstens {fmt_num(MAX_DEBT_TO_EQUITY, 2)} – also Schulden maximal 33 % des "
                     "Eigenkapitals. Fehlen die Daten, steht die Aktie auf „❔ Prüfen“."),
        ("Ergebnis", "✅ Halal nur, wenn beides passt. ❌ Nicht halal, wenn ein Kriterium verletzt ist."),
    ]))
    st.markdown("""
**Wichtig zu wissen**
- Das ist eine **vereinfachte Prüfung zur Orientierung**. Vollständige Shariah-Screenings prüfen zusätzlich z. B.
  Zinseinnahmen, Bargeld und verzinsliche Anlagen und den Umsatzanteil aus nicht erlaubten Quellen (meist < 5 %).
- Die Schuldengrenze der App ist **streng**: Viele islamische Indizes teilen die Schulden durch den Börsenwert statt
  durch das Eigenkapital – dort bestehen mehr Aktien.
- Für verbindliche Entscheidungen nutze einen spezialisierten Halal-Screener oder frage eine Fatwa-Stelle.
- Short-Selling und Hebelprodukte sind nach gängiger Auffassung nicht halal. „Verkaufen“ heißt in dieser App nur: die
  Aktie nicht (mehr) halten.

**Märkte:** 🇺🇸 USA, 🇪🇺 Europa und 🇨🇳 China. Chinesische Aktien werden mit den Kursen ihrer Heimatbörse Hongkong
analysiert und sind in Europa in Euro handelbar (z. B. Tradegate, Frankfurt, Neobroker). Alle Preise werden für den
Vergleich in Euro umgerechnet.
""")

    html(ui.section("📈 So entsteht die Empfehlung"))
    html(ui.steps([
        ("Kurse laden", "Tägliche Schlusskurse der letzten Jahre von Yahoo Finance – für die Aktie und den Index."),
        ("Sieben Faktoren", "Trend, Momentum, RSI, 52-Wochen-Hoch, Volumen, relative Stärke und Marktumfeld werden je "
                            "von −100 bis +100 bewertet."),
        ("Score & Stufe", "Der gewichtete Durchschnitt ergibt den Signal-Score. Die Schwellen ±25 und ±55 entscheiden "
                          "über die fünf Stufen."),
        ("Termine & Kurse", "Verkaufsdatum bzw. Haltedauer, Kursziel, Stop-Loss und Preis-Schwellen kommen aus Trend, "
                            "Schwankung und der Historie der Aktie."),
    ]))
    weights = "\n".join(f"| {COMPONENT_LABELS[k]} | {fmt_num(w * 100, 0)} % |" for k, w in WEIGHTS.items())
    st.markdown(f"""
| Signal-Score | Empfehlung | Was die App zusätzlich sagt |
|---|---|---|
| ab {STRONG_BUY_THRESHOLD:+.0f} | {label_text("STRONG_BUY")} | Verkauf ab Datum, Kursziel, Stop-Loss |
| {BUY_THRESHOLD:+.0f} bis {STRONG_BUY_THRESHOLD:+.0f} | {label_text("BUY")} | Verkauf ab Datum, Kursziel, Stop-Loss |
| {SELL_THRESHOLD:+.0f} bis {BUY_THRESHOLD:+.0f} | {label_text("HOLD")} | Halten bis Datum, Kurse für Kauf-/Verkaufssignal |
| {STRONG_SELL_THRESHOLD:+.0f} bis {SELL_THRESHOLD:+.0f} | {label_text("SELL")} | Neubewertung ab Datum |
| bis {STRONG_SELL_THRESHOLD:+.0f} | {label_text("STRONG_SELL")} | Neubewertung ab Datum |

| Faktor | Gewicht |
|---|---|
{weights}

- **Stop-Loss** = Kurs − 2 × ATR (durchschnittliche Tagesschwankung). **Kursziel** = vorsichtig fortgeschriebener
  Trend der letzten 6 Monate, mindestens Kurs + 3 × ATR.
- **Kennzahlen** (KGV, Debt-to-Equity …) fließen nicht in den Score ein, sondern in den Halal-Check und die Ampeln.
- Alle Termine und Kursziele sind **Richtwerte**, keine Prognosen mit Gewähr. **Keine Anlageberatung.**
""")
    st.caption(f"Stand der Kursdaten: {fmt_date(max((r.as_of for r in recs), default=None))}")
