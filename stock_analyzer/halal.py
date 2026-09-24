"""Halal (Shariah) screen with two criteria:

1. Business activity: no alcohol, tobacco, weapons, gambling, interest-based
   finance (banks, lenders), conventional insurance, pork or adult entertainment.
   Cases that scholars judge differently (e.g. music/film entertainment, crypto,
   small defence shares) are marked "prüfen".
2. Debt: debt-to-equity must not exceed 33 %.

The business classification of the stocks in the app's lists was reviewed by
hand; for other stocks the Yahoo Finance industry is used. This is a simplified
screen for orientation – it does not replace a full Shariah audit (which also
checks e.g. interest income and cash holdings).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .formatting import fmt_num
from .fundamentals import Fundamentals
from .universes import CATALOG

MAX_DEBT_TO_EQUITY = 0.33

HALAL, NOT_HALAL, CHECK = "halal", "nicht", "pruefen"

CATEGORY = {
    "alkohol": "🍺 Alkohol",
    "tabak": "🚬 Tabak",
    "waffen": "🔫 Waffen & Rüstung",
    "gluecksspiel": "🎰 Glücksspiel & Wetten",
    "zinsen": "🏦 Zinsgeschäft (Banken & Kredite)",
    "versicherung": "🛡️ Konventionelle Versicherung",
    "schwein": "🐖 Schweinefleisch",
    "erwachsene": "🔞 Erwachsenenunterhaltung",
    "unterhaltung": "🎬 Musik/Film-Unterhaltung (je nach Auslegung)",
    "hotel": "🏨 Hotels mit Alkoholausschank",
    "krypto": "₿ Krypto-Geschäft (umstritten)",
}

# Reviewed business activity: ticker -> (verdict, category). Stocks of the app's
# lists that are not listed here have a permissible core business.
BUSINESS: dict[str, tuple[str, str]] = {
    # banks, lenders, asset managers
    **{t: (NOT_HALAL, "zinsen") for t in (
        "JPM", "BAC", "WFC", "C", "GS", "MS", "SCHW", "BLK", "AXP",
        "DBK.DE", "CBK.DE", "BNP.PA", "SAN.MC", "BBVA.MC", "UCG.MI", "ISP.MI", "INGA.AS", "HSBA.L", "UBSG.SW",
        "1398.HK", "0939.HK",
    )},
    # conventional insurance
    **{t: (NOT_HALAL, "versicherung") for t in (
        "BRK-B", "ALV.DE", "MUV2.DE", "HNR1.DE", "TLX.DE", "CS.PA", "2318.HK", "1299.HK",
    )},
    # weapons and defence (defence share clearly above 5 % of revenue)
    **{t: (NOT_HALAL, "waffen") for t in (
        "LMT", "RTX", "BA", "GE", "AXON", "RHM.DE", "HAG.DE", "R3NK.DE", "AIR.DE", "AIR.PA", "SAF.PA", "MTX.DE",
        "RR.L",
    )},
    # alcohol
    **{t: (NOT_HALAL, "alkohol") for t in ("ABI.BR", "RI.PA", "MC.PA", "0168.HK", "0291.HK", "1876.HK")},
    # tobacco
    "PM": (NOT_HALAL, "tabak"),
    "MO": (NOT_HALAL, "tabak"),
    # gambling
    "0027.HK": (NOT_HALAL, "gluecksspiel"),
    "1928.HK": (NOT_HALAL, "gluecksspiel"),
    # judged differently by scholars -> check yourself
    "HON": (CHECK, "waffen"),
    "PLTR": (CHECK, "waffen"),
    "TKA.DE": (CHECK, "waffen"),
    "PYPL": (CHECK, "zinsen"),
    "DB1.DE": (CHECK, "zinsen"),
    "0388.HK": (CHECK, "zinsen"),
    "COIN": (CHECK, "krypto"),
    "MSTR": (CHECK, "krypto"),
    "NFLX": (CHECK, "unterhaltung"),
    "DIS": (CHECK, "unterhaltung"),
    "WBD": (CHECK, "unterhaltung"),
    "EVD.DE": (CHECK, "unterhaltung"),
    "RRTL.DE": (CHECK, "unterhaltung"),
    "MAR": (CHECK, "hotel"),
    "6862.HK": (CHECK, "schwein"),
}

# Fallback for stocks outside the app's lists: Yahoo Finance industry keywords.
INDUSTRY_RULES: list[tuple[str, str, str]] = [
    ("brewers", NOT_HALAL, "alkohol"),
    ("wineries", NOT_HALAL, "alkohol"),
    ("distillers", NOT_HALAL, "alkohol"),
    ("tobacco", NOT_HALAL, "tabak"),
    ("gambling", NOT_HALAL, "gluecksspiel"),
    ("casino", NOT_HALAL, "gluecksspiel"),
    ("banks", NOT_HALAL, "zinsen"),
    ("mortgage", NOT_HALAL, "zinsen"),
    ("insurance", NOT_HALAL, "versicherung"),
    ("financial conglomerates", NOT_HALAL, "zinsen"),
    ("credit services", CHECK, "zinsen"),
    ("capital markets", CHECK, "zinsen"),
    ("asset management", CHECK, "zinsen"),
    ("aerospace & defense", CHECK, "waffen"),
    ("lodging", CHECK, "hotel"),
]


@dataclass
class HalalCheck:
    status: str
    business_status: str
    business_reason: str
    debt_status: str
    debt_reason: str
    reasons: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return {HALAL: "Halal", NOT_HALAL: "Nicht halal", CHECK: "Prüfen"}[self.status]

    @property
    def icon(self) -> str:
        return {HALAL: "✅", NOT_HALAL: "❌", CHECK: "❔"}[self.status]


def business_screen(ticker: str, sector: str | None, industry: str | None) -> tuple[str, str | None]:
    """(verdict, category) for the company's business activity."""
    if ticker in BUSINESS:
        return BUSINESS[ticker]
    if ticker in CATALOG:
        return HALAL, None
    text = f"{industry or ''} {sector or ''}".lower()
    for keyword, verdict, category in INDUSTRY_RULES:
        if keyword in text:
            return verdict, category
    if not text.strip():
        return CHECK, None
    return HALAL, None


def check(ticker: str, fundamentals: Fundamentals | None) -> HalalCheck:
    f = fundamentals or Fundamentals(ticker)
    verdict, category = business_screen(ticker, f.sector, f.industry)
    if verdict == HALAL:
        business_reason = "Kein verbotenes Geschäftsfeld"
    elif category:
        business_reason = CATEGORY[category]
    else:
        business_reason = "Geschäftsfeld unbekannt"

    de = f.debt_to_equity
    if de is None:
        debt_status, debt_reason = CHECK, "Verschuldung unbekannt (keine Daten)"
    elif de < 0:
        debt_status, debt_reason = NOT_HALAL, "Negatives Eigenkapital"
    elif de > MAX_DEBT_TO_EQUITY:
        debt_status, debt_reason = NOT_HALAL, f"Zu hohe Schulden: Debt-to-Equity {fmt_num(de, 2)} > 0,33"
    else:
        debt_status, debt_reason = HALAL, f"Debt-to-Equity {fmt_num(de, 2)} ≤ 0,33"

    statuses = (verdict, debt_status)
    status = NOT_HALAL if NOT_HALAL in statuses else CHECK if CHECK in statuses else HALAL
    reasons = [r for s, r in ((verdict, business_reason), (debt_status, debt_reason)) if s != HALAL]
    return HalalCheck(status, verdict, business_reason, debt_status, debt_reason, reasons)
