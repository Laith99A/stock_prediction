"""Fundamental key figures (P/E, P/B, debt-to-equity, …) with a traffic-light rating.

Data comes from Yahoo Finance (`yfinance.Ticker.info`). The ratings use general
rules of thumb; what counts as "cheap" differs between sectors, so they are a
first orientation, not a verdict.
"""
from __future__ import annotations

import math
import zlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

import numpy as np

from .formatting import fmt_num, fmt_pct

FINANCIAL_SECTORS = {"Financial Services", "Financial", "Banks", "Insurance"}


@dataclass
class Fundamentals:
    ticker: str
    name: str | None = None
    currency: str | None = None
    sector: str | None = None
    industry: str | None = None
    price: float | None = None
    market_cap: float | None = None
    pe: float | None = None
    forward_pe: float | None = None
    peg: float | None = None
    pb: float | None = None
    ps: float | None = None
    ev_ebitda: float | None = None
    debt_to_equity: float | None = None  # ratio: 1.5 means debt is 150 % of equity
    current_ratio: float | None = None
    roe: float | None = None
    profit_margin: float | None = None
    revenue_growth: float | None = None
    earnings_growth: float | None = None
    dividend_yield: float | None = None
    payout_ratio: float | None = None
    beta: float | None = None
    eps: float | None = None
    target_price: float | None = None
    analyst_rating: str | None = None
    analysts: int | None = None
    # company profile
    summary: str | None = None
    employees: int | None = None
    city: str | None = None
    country: str | None = None
    website: str | None = None
    is_demo: bool = False

    @property
    def is_financial(self) -> bool:
        return (self.sector or "") in FINANCIAL_SECTORS

    @property
    def available(self) -> bool:
        return any(v is not None for v in (self.pe, self.pb, self.debt_to_equity, self.market_cap, self.roe))


def _num(info: dict, *keys: str) -> float | None:
    for key in keys:
        value = info.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
            return float(value)
    return None


def parse_info(ticker: str, info: dict) -> Fundamentals:
    """Map a Yahoo Finance `info` dict to Fundamentals (with unit fixes)."""
    price = _num(info, "currentPrice", "regularMarketPrice", "previousClose")

    # Yahoo reports debt-to-equity in percent (150.0 = 1.5x).
    de = _num(info, "debtToEquity")
    if de is not None:
        de /= 100.0
    else:
        debt, book, shares = _num(info, "totalDebt"), _num(info, "bookValue"), _num(info, "sharesOutstanding")
        if debt is not None and book and shares:
            de = debt / (book * shares)

    # Dividend yield: derive from the annual dividend where possible, because the
    # unit of Yahoo's "dividendYield" field has changed over time.
    rate = _num(info, "dividendRate", "trailingAnnualDividendRate")
    if rate is not None and price:
        dividend_yield = rate / price
    else:
        dividend_yield = _num(info, "trailingAnnualDividendYield")
        # Yahoo omits the dividend fields for companies that pay none.
        if dividend_yield is None and price and not any(k in info for k in ("dividendRate", "dividendYield")):
            dividend_yield = 0.0

    analysts = _num(info, "numberOfAnalystOpinions")
    employees = _num(info, "fullTimeEmployees")
    website = info.get("website") if isinstance(info.get("website"), str) else None
    if website and not website.startswith(("http://", "https://")):
        website = "https://" + website
    return Fundamentals(
        ticker=ticker,
        name=info.get("longName") or info.get("shortName"),
        currency=info.get("currency"),
        sector=info.get("sector"),
        industry=info.get("industry"),
        price=price,
        market_cap=_num(info, "marketCap"),
        pe=_num(info, "trailingPE"),
        forward_pe=_num(info, "forwardPE"),
        peg=_num(info, "trailingPegRatio", "pegRatio"),
        pb=_num(info, "priceToBook"),
        ps=_num(info, "priceToSalesTrailing12Months"),
        ev_ebitda=_num(info, "enterpriseToEbitda"),
        debt_to_equity=de,
        current_ratio=_num(info, "currentRatio"),
        roe=_num(info, "returnOnEquity"),
        profit_margin=_num(info, "profitMargins"),
        revenue_growth=_num(info, "revenueGrowth"),
        earnings_growth=_num(info, "earningsGrowth", "earningsQuarterlyGrowth"),
        dividend_yield=dividend_yield,
        payout_ratio=_num(info, "payoutRatio"),
        beta=_num(info, "beta"),
        eps=_num(info, "trailingEps"),
        target_price=_num(info, "targetMeanPrice"),
        analyst_rating=info.get("recommendationKey") if info.get("recommendationKey") not in (None, "none") else None,
        analysts=int(analysts) if analysts is not None else None,
        summary=info.get("longBusinessSummary") or None,
        employees=int(employees) if employees is not None else None,
        city=info.get("city") or None,
        country=info.get("country") or None,
        website=website,
    )


def fetch_fundamentals(ticker: str) -> Fundamentals:
    """Key figures from Yahoo Finance; empty Fundamentals if unavailable."""
    import yfinance as yf

    try:
        info = yf.Ticker(ticker).info or {}
    except Exception:
        info = {}
    return parse_info(ticker, info)


def fetch_many(tickers: list[str], workers: int = 4) -> dict[str, Fundamentals]:
    """Fetch several tickers in parallel (Yahoo allows only moderate parallelism)."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return dict(zip(tickers, pool.map(fetch_fundamentals, tickers)))


def synthetic_fundamentals(ticker: str, price: float | None = None) -> Fundamentals:
    """Plausible, reproducible key figures for the offline demo mode."""
    rng = np.random.default_rng(zlib.crc32(("fund-" + ticker).encode()))
    pe = float(rng.choice([rng.uniform(6, 14), rng.uniform(14, 26), rng.uniform(26, 60), -1.0], p=[.3, .4, .25, .05]))
    growth = float(rng.normal(0.07, 0.12))
    return Fundamentals(
        ticker=ticker,
        sector=str(rng.choice(["Technology", "Industrials", "Consumer Cyclical", "Healthcare", "Financial Services"])),
        price=price,
        market_cap=float(10 ** rng.uniform(9.3, 12.3)),
        pe=pe if pe > 0 else None,
        forward_pe=float(pe * rng.uniform(0.75, 1.0)) if pe > 0 else float(rng.uniform(20, 60)),
        peg=float(rng.uniform(0.6, 3.2)),
        pb=float(rng.lognormal(0.9, 0.7)),
        ps=float(rng.lognormal(0.8, 0.8)),
        ev_ebitda=float(rng.uniform(5, 30)),
        debt_to_equity=float(rng.choice([rng.uniform(0.05, 0.5), rng.uniform(0.5, 1.5), rng.uniform(1.5, 3.5)],
                                        p=[.4, .4, .2])),
        current_ratio=float(rng.uniform(0.7, 2.8)),
        roe=float(rng.normal(0.14, 0.1)),
        profit_margin=float(rng.normal(0.11, 0.09)),
        revenue_growth=growth,
        earnings_growth=float(growth + rng.normal(0, 0.1)),
        dividend_yield=float(max(rng.normal(0.02, 0.015), 0.0)),
        payout_ratio=float(rng.uniform(0.0, 0.9)),
        beta=float(rng.uniform(0.5, 1.8)),
        target_price=float(price * rng.uniform(0.85, 1.3)) if price else None,
        analyst_rating=str(rng.choice(["strong_buy", "buy", "hold", "underperform"], p=[.2, .45, .3, .05])),
        analysts=int(rng.integers(5, 45)),
        is_demo=True,
    )


# ---------------------------------------------------------------------------- rating

GOOD, OK, BAD, INFO, NA = "good", "ok", "bad", "info", "na"

BEWERTUNG = "Bewertung – ist die Aktie teuer?"
SCHULDEN = "Verschuldung & Stabilität"
ERTRAG = "Profitabilität & Wachstum"
DIVIDENDE = "Dividende, Risiko & Größe"
GROUPS = [SCHULDEN, BEWERTUNG, ERTRAG, DIVIDENDE]


@dataclass
class Metric:
    key: str  # glossary key
    title: str
    group: str
    value: float | None
    text: str
    status: str
    verdict: str
    rule: str
    highlight: bool = False


@dataclass
class GroupSummary:
    group: str
    status: str
    verdict: str
    metrics: list[Metric] = field(default_factory=list)


def _bands(value: float | None, bands: list[tuple[float, str, str]], above: tuple[str, str]) -> tuple[str, str]:
    """First band whose upper limit exceeds value -> (status, verdict)."""
    if value is None:
        return NA, "keine Daten"
    for limit, status, verdict in bands:
        if value < limit:
            return status, verdict
    return above


def _ratio(v: float | None, digits: int = 1) -> str:
    return "–" if v is None else fmt_num(v, digits)


def _big(v: float | None) -> str:
    if v is None:
        return "–"
    for unit, size in (("Bio.", 1e12), ("Mrd.", 1e9), ("Mio.", 1e6)):
        if abs(v) >= size:
            return f"{fmt_num(v / size, 1)} {unit}"
    return fmt_num(v, 0)


_ANALYST = {"strong_buy": "Stark kaufen", "buy": "Kaufen", "hold": "Halten", "underperform": "Unterdurchschnittlich",
            "sell": "Verkaufen", "strong_sell": "Stark verkaufen"}


def rate(f: Fundamentals) -> list[Metric]:
    """All key figures with value, traffic-light status and a rule of thumb."""
    m: list[Metric] = []

    # --- debt & stability
    de = f.debt_to_equity
    if f.is_financial and de is not None:
        status, verdict = INFO, "bei Banken/Versicherern kaum vergleichbar"
    elif de is not None and de < 0:
        status, verdict = BAD, "negatives Eigenkapital"
    else:
        status, verdict = _bands(de, [(0.5, GOOD, "niedrig verschuldet"), (1.0, GOOD, "solide"),
                                      (2.0, OK, "erhöht"), ], (BAD, "hoch verschuldet"))
    m.append(Metric("verschuldungsgrad", "Verschuldungsgrad (Debt-to-Equity)", SCHULDEN, de,
                    _ratio(de, 2), status, verdict,
                    "unter 1 solide · 1–2 erhöht · über 2 hoch verschuldet", highlight=True))
    status, verdict = _bands(f.current_ratio, [(1.0, BAD, "knapp"), (1.5, OK, "ausreichend")], (GOOD, "komfortabel"))
    if f.is_financial and f.current_ratio is not None:
        status, verdict = INFO, "bei Banken nicht aussagekräftig"
    m.append(Metric("liquiditaet", "Liquidität (Current Ratio)", SCHULDEN, f.current_ratio, _ratio(f.current_ratio, 2),
                    status, verdict, "über 1,5 komfortabel · 1–1,5 ausreichend · unter 1 knapp"))

    # --- valuation
    if f.pe is None and f.eps is not None and f.eps < 0:
        m.append(Metric("kgv", "KGV (Kurs-Gewinn-Verhältnis)", BEWERTUNG, None, "–", BAD, "Verlust – kein KGV",
                        "unter 15 günstig · 15–25 fair · über 25 teuer"))
    else:
        s, v = _bands(f.pe, [(0, BAD, "Verlust"), (15, GOOD, "günstig"), (25, OK, "fair"), (40, BAD, "teuer")],
                      (BAD, "sehr teuer"))
        m.append(Metric("kgv", "KGV (Kurs-Gewinn-Verhältnis)", BEWERTUNG, f.pe, _ratio(f.pe), s, v,
                        "unter 15 günstig · 15–25 fair · über 25 teuer"))
    s, v = _bands(f.forward_pe, [(0, BAD, "Verlust erwartet"), (15, GOOD, "günstig"), (25, OK, "fair")], (BAD, "teuer"))
    m.append(Metric("kgv_erwartet", "Erwartetes KGV (Forward P/E)", BEWERTUNG, f.forward_pe, _ratio(f.forward_pe), s, v,
                    "wie KGV, aber mit dem erwarteten Gewinn der nächsten 12 Monate"))
    s, v = _bands(f.peg, [(0, INFO, "nicht sinnvoll"), (1.0, GOOD, "günstig"), (2.0, OK, "fair")], (BAD, "teuer"))
    m.append(Metric("peg", "PEG-Ratio", BEWERTUNG, f.peg, _ratio(f.peg, 2), s, v,
                    "unter 1 günstig · 1–2 fair · über 2 teuer (KGV im Verhältnis zum Wachstum)"))
    s, v = _bands(f.pb, [(0, BAD, "negatives Eigenkapital"), (1.0, GOOD, "unter Buchwert"), (3.0, OK, "fair")],
                  (BAD, "teuer"))
    m.append(Metric("kbv", "KBV (Kurs-Buchwert-Verhältnis, P/B)", BEWERTUNG, f.pb, _ratio(f.pb, 2), s, v,
                    "unter 1 günstig · 1–3 fair · über 3 teuer"))
    s, v = _bands(f.ps, [(1.0, GOOD, "günstig"), (4.0, OK, "fair")], (BAD, "teuer"))
    m.append(Metric("kuv", "KUV (Kurs-Umsatz-Verhältnis, P/S)", BEWERTUNG, f.ps, _ratio(f.ps, 2), s, v,
                    "unter 1 günstig · 1–4 fair · über 4 teuer"))
    s, v = _bands(f.ev_ebitda, [(0, BAD, "negativ"), (8, GOOD, "günstig"), (15, OK, "fair")], (BAD, "teuer"))
    m.append(Metric("ev_ebitda", "EV/EBITDA", BEWERTUNG, f.ev_ebitda, _ratio(f.ev_ebitda), s, v,
                    "unter 8 günstig · 8–15 fair · über 15 teuer"))

    # --- profitability & growth
    s, v = _bands(f.roe, [(0, BAD, "Verlust"), (0.08, BAD, "schwach"), (0.15, OK, "ordentlich")], (GOOD, "stark"))
    m.append(Metric("eigenkapitalrendite", "Eigenkapitalrendite (ROE)", ERTRAG, f.roe, fmt_pct(f.roe, 1, sign=False),
                    s, v, "über 15 % stark · 8–15 % ordentlich · unter 8 % schwach"))
    s, v = _bands(f.profit_margin, [(0, BAD, "Verlust"), (0.05, BAD, "dünn"), (0.15, OK, "ordentlich")],
                  (GOOD, "hoch"))
    m.append(Metric("nettomarge", "Nettomarge", ERTRAG, f.profit_margin, fmt_pct(f.profit_margin, 1, sign=False),
                    s, v, "über 15 % hoch · 5–15 % ordentlich · unter 5 % dünn"))
    s, v = _bands(f.revenue_growth, [(0, BAD, "schrumpfend"), (0.10, OK, "moderat")], (GOOD, "stark"))
    m.append(Metric("umsatzwachstum", "Umsatzwachstum (zum Vorjahr)", ERTRAG, f.revenue_growth,
                    fmt_pct(f.revenue_growth), s, v, "über 10 % stark · 0–10 % moderat · negativ schrumpfend"))
    s, v = _bands(f.earnings_growth, [(0, BAD, "rückläufig"), (0.10, OK, "moderat")], (GOOD, "stark"))
    m.append(Metric("gewinnwachstum", "Gewinnwachstum (zum Vorjahr)", ERTRAG, f.earnings_growth,
                    fmt_pct(f.earnings_growth), s, v, "über 10 % stark · 0–10 % moderat · negativ rückläufig"))

    # --- dividend, risk, size
    dy = f.dividend_yield
    if dy is None:
        s, v = NA, "keine Daten"
    elif dy == 0:
        s, v = INFO, "keine Dividende"
    else:
        s, v = _bands(dy, [(0.02, OK, "niedrig"), (0.06, GOOD, "attraktiv")], (OK, "sehr hoch – Nachhaltigkeit prüfen"))
    m.append(Metric("dividendenrendite", "Dividendenrendite", DIVIDENDE, dy, fmt_pct(dy, 2, sign=False), s, v,
                    "2–6 % attraktiv · über 6 % prüfen, ob sie gehalten werden kann"))
    s, v = _bands(f.payout_ratio, [(0.01, INFO, "keine Ausschüttung"), (0.6, GOOD, "gut gedeckt"),
                                   (0.9, OK, "hoch")], (BAD, "nicht gedeckt"))
    m.append(Metric("ausschuettungsquote", "Ausschüttungsquote", DIVIDENDE, f.payout_ratio,
                    fmt_pct(f.payout_ratio, 0, sign=False), s, v, "unter 60 % gut gedeckt · über 90 % riskant"))
    s, v = _bands(f.beta, [(0.8, INFO, "ruhiger als der Markt"), (1.2, INFO, "wie der Markt")],
                  (INFO, "schwankungsfreudiger als der Markt"))
    m.append(Metric("beta", "Beta", DIVIDENDE, f.beta, _ratio(f.beta, 2), s, v,
                    "1 = schwankt wie der Markt · über 1 stärker · unter 1 ruhiger"))
    cap = f.market_cap
    size = None if cap is None else ("Large Cap (groß)" if cap >= 10e9 else "Mid Cap (mittel)" if cap >= 2e9
                                     else "Small Cap (klein)")
    m.append(Metric("marktkapitalisierung", "Börsenwert (Marktkapitalisierung)", DIVIDENDE, cap,
                    _big(cap), INFO if cap else NA, size or "keine Daten", "über 10 Mrd. groß · 2–10 Mrd. mittel"))
    if f.target_price and f.price:
        upside = f.target_price / f.price - 1
        rating = _ANALYST.get(f.analyst_rating or "", "")
        verdict = f"{fmt_pct(upside, 0)} Potenzial" + (f" · Konsens: {rating}" if rating else "")
        m.append(Metric("analystenziel", "Ø Kursziel der Analysten", DIVIDENDE, f.target_price,
                        fmt_num(f.target_price), INFO, verdict,
                        f"Durchschnitt von {f.analysts or '?'} Analysten – oft zu optimistisch"))
    return m


def summarize(metrics: list[Metric]) -> list[GroupSummary]:
    """One traffic light per group from the rated metrics."""
    names = {
        SCHULDEN: {GOOD: "solide finanziert", OK: "etwas erhöhte Verschuldung", BAD: "angespannte Finanzen"},
        BEWERTUNG: {GOOD: "eher günstig", OK: "fair bewertet", BAD: "eher teuer"},
        ERTRAG: {GOOD: "profitabel & wachsend", OK: "durchwachsen", BAD: "schwach"},
    }
    out = []
    for group in GROUPS:
        items = [x for x in metrics if x.group == group]
        rated = [x for x in items if x.status in (GOOD, OK, BAD)]
        if not rated:
            out.append(GroupSummary(group, INFO if items else NA, "nur Info-Werte" if items else "keine Daten", items))
            continue
        # Debt-to-equity dominates the stability verdict.
        if group == SCHULDEN and items[0].status in (GOOD, OK, BAD):
            status = items[0].status
        elif group == DIVIDENDE:
            dividend, payout = items[0], items[1]
            if dividend.status not in (GOOD, OK, BAD):
                out.append(GroupSummary(group, INFO, dividend.verdict, items))
                continue
            status = BAD if payout.status == BAD else dividend.status
            verdict = f"Dividende {dividend.verdict}" + (", nicht gedeckt" if payout.status == BAD else "")
            out.append(GroupSummary(group, status, verdict, items))
            continue
        else:
            points = sum({GOOD: 1, OK: 0, BAD: -1}[x.status] for x in rated) / len(rated)
            status = GOOD if points > 0.33 else BAD if points < -0.33 else OK
        out.append(GroupSummary(group, status, names[group][status], items))
    return out
