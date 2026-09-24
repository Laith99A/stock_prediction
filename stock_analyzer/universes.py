"""Stock lists for the three markets (USA, Europe, China), a searchable catalog
and name search. All tickers are Yahoo Finance symbols.

Chinese companies are analysed with the prices of their home listing in Hong
Kong (or the US listing for NIO and PDD). The same shares are tradable in Europe,
e.g. on Tradegate, Frankfurt or via neobrokers.

Index memberships change over time; the lists are a starting point and can be
edited freely. Other stocks can be found through the Yahoo Finance search.
"""
from __future__ import annotations

import unicodedata

DAX = {
    "ADS.DE": "adidas",
    "AIR.DE": "Airbus",
    "ALV.DE": "Allianz",
    "BAS.DE": "BASF",
    "BAYN.DE": "Bayer",
    "BEI.DE": "Beiersdorf",
    "BMW.DE": "BMW",
    "BNR.DE": "Brenntag",
    "CBK.DE": "Commerzbank",
    "CON.DE": "Continental",
    "DB1.DE": "Deutsche Börse",
    "DBK.DE": "Deutsche Bank",
    "DHL.DE": "DHL Group (Deutsche Post)",
    "DTE.DE": "Deutsche Telekom",
    "DTG.DE": "Daimler Truck",
    "ENR.DE": "Siemens Energy",
    "EOAN.DE": "E.ON",
    "FME.DE": "Fresenius Medical Care",
    "FRE.DE": "Fresenius",
    "G1A.DE": "GEA Group",
    "HEI.DE": "Heidelberg Materials",
    "HEN3.DE": "Henkel",
    "HNR1.DE": "Hannover Rück",
    "IFX.DE": "Infineon",
    "MBG.DE": "Mercedes-Benz",
    "MRK.DE": "Merck KGaA",
    "MTX.DE": "MTU Aero Engines",
    "MUV2.DE": "Münchener Rück (Munich Re)",
    "PAH3.DE": "Porsche SE",
    "QIA.DE": "Qiagen",
    "RHM.DE": "Rheinmetall",
    "RWE.DE": "RWE",
    "SAP.DE": "SAP",
    "SHL.DE": "Siemens Healthineers",
    "SIE.DE": "Siemens",
    "SRT3.DE": "Sartorius",
    "SY1.DE": "Symrise",
    "VNA.DE": "Vonovia",
    "VOW3.DE": "Volkswagen (VW)",
    "ZAL.DE": "Zalando",
}

MDAX = {
    "1U1.DE": "1&1",
    "AFX.DE": "Carl Zeiss Meditec",
    "AIXA.DE": "Aixtron",
    "BC8.DE": "Bechtle",
    "BOSS.DE": "Hugo Boss",
    "DHER.DE": "Delivery Hero",
    "DWNI.DE": "Deutsche Wohnen",
    "EVD.DE": "CTS Eventim",
    "EVK.DE": "Evonik",
    "FNTN.DE": "freenet",
    "FRA.DE": "Fraport",
    "G24.DE": "Scout24",
    "GXI.DE": "Gerresheimer",
    "HAG.DE": "Hensoldt",
    "HFG.DE": "HelloFresh",
    "HOT.DE": "Hochtief",
    "JUN3.DE": "Jungheinrich",
    "KBX.DE": "Knorr-Bremse",
    "KGX.DE": "Kion",
    "KRN.DE": "Krones",
    "LEG.DE": "LEG Immobilien",
    "LHA.DE": "Lufthansa",
    "LXS.DE": "Lanxess",
    "NDX1.DE": "Nordex",
    "NEM.DE": "Nemetschek",
    "P911.DE": "Porsche AG",
    "PUM.DE": "Puma",
    "R3NK.DE": "Renk",
    "RAA.DE": "Rational",
    "RRTL.DE": "RTL Group",
    "SAX.DE": "Ströer",
    "SDF.DE": "K+S",
    "TEG.DE": "TAG Immobilien",
    "TKA.DE": "thyssenkrupp",
    "TLX.DE": "Talanx",
    "TMV.DE": "TeamViewer",
    "TUI1.DE": "TUI",
    "UTDI.DE": "United Internet",
    "WAF.DE": "Siltronic",
    "8TRA.DE": "Traton",
}

EUROPE = {
    "ASML.AS": "ASML",
    "MC.PA": "LVMH",
    "SAP.DE": "SAP",
    "NOVO-B.CO": "Novo Nordisk",
    "NESN.SW": "Nestlé",
    "ROG.SW": "Roche",
    "NOVN.SW": "Novartis",
    "UBSG.SW": "UBS",
    "AZN.L": "AstraZeneca",
    "SHEL.L": "Shell",
    "HSBA.L": "HSBC",
    "ULVR.L": "Unilever",
    "BP.L": "BP",
    "RR.L": "Rolls-Royce",
    "TTE.PA": "TotalEnergies",
    "SAN.PA": "Sanofi",
    "OR.PA": "L'Oréal",
    "RMS.PA": "Hermès",
    "SU.PA": "Schneider Electric",
    "AI.PA": "Air Liquide",
    "AIR.PA": "Airbus",
    "SAF.PA": "Safran",
    "BNP.PA": "BNP Paribas",
    "CS.PA": "AXA",
    "EL.PA": "EssilorLuxottica",
    "DG.PA": "Vinci",
    "KER.PA": "Kering",
    "BN.PA": "Danone",
    "RI.PA": "Pernod Ricard",
    "SGO.PA": "Saint-Gobain",
    "IBE.MC": "Iberdrola",
    "SAN.MC": "Banco Santander",
    "BBVA.MC": "BBVA",
    "ITX.MC": "Inditex (Zara)",
    "UCG.MI": "UniCredit",
    "ISP.MI": "Intesa Sanpaolo",
    "ENEL.MI": "Enel",
    "ENI.MI": "Eni",
    "RACE.MI": "Ferrari",
    "STLAM.MI": "Stellantis",
    "INGA.AS": "ING",
    "ADYEN.AS": "Adyen",
    "PRX.AS": "Prosus",
    "AD.AS": "Ahold Delhaize",
    "WKL.AS": "Wolters Kluwer",
    "ABI.BR": "Anheuser-Busch InBev",
    "NOKIA.HE": "Nokia",
    "SIE.DE": "Siemens",
    "ALV.DE": "Allianz",
    "DTE.DE": "Deutsche Telekom",
    "MUV2.DE": "Münchener Rück (Munich Re)",
    "RHM.DE": "Rheinmetall",
}

US_TOP = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet (Google)",
    "META": "Meta Platforms (Facebook)",
    "AVGO": "Broadcom",
    "TSLA": "Tesla",
    "BRK-B": "Berkshire Hathaway",
    "JPM": "JPMorgan Chase",
    "LLY": "Eli Lilly",
    "V": "Visa",
    "MA": "Mastercard",
    "UNH": "UnitedHealth",
    "XOM": "Exxon Mobil",
    "COST": "Costco",
    "WMT": "Walmart",
    "HD": "Home Depot",
    "PG": "Procter & Gamble",
    "JNJ": "Johnson & Johnson",
    "NFLX": "Netflix",
    "ORCL": "Oracle",
    "BAC": "Bank of America",
    "ABBV": "AbbVie",
    "CRM": "Salesforce",
    "CVX": "Chevron",
    "KO": "Coca-Cola",
    "MRK": "Merck & Co.",
    "AMD": "AMD",
    "PEP": "PepsiCo",
    "ADBE": "Adobe",
    "TMO": "Thermo Fisher",
    "LIN": "Linde",
    "CSCO": "Cisco",
    "ACN": "Accenture",
    "MCD": "McDonald's",
    "WFC": "Wells Fargo",
    "ABT": "Abbott",
    "IBM": "IBM",
    "PM": "Philip Morris",
    "GE": "GE Aerospace",
    "QCOM": "Qualcomm",
    "TXN": "Texas Instruments",
    "INTU": "Intuit",
    "CAT": "Caterpillar",
    "NOW": "ServiceNow",
    "VZ": "Verizon",
    "AMGN": "Amgen",
    "DIS": "Walt Disney",
    "ISRG": "Intuitive Surgical",
    "GS": "Goldman Sachs",
    "T": "AT&T",
    "PFE": "Pfizer",
    "SPGI": "S&P Global",
    "AMAT": "Applied Materials",
    "UBER": "Uber",
    "RTX": "RTX (Raytheon)",
    "NEE": "NextEra Energy",
    "CMCSA": "Comcast",
    "UNP": "Union Pacific",
    "LOW": "Lowe's",
    "BKNG": "Booking Holdings",
    "HON": "Honeywell",
    "AXP": "American Express",
    "MS": "Morgan Stanley",
    "BLK": "BlackRock",
    "COP": "ConocoPhillips",
    "TJX": "TJX",
    "C": "Citigroup",
    "BA": "Boeing",
    "SCHW": "Charles Schwab",
    "VRTX": "Vertex Pharmaceuticals",
    "LMT": "Lockheed Martin",
    "ADP": "ADP",
    "MDT": "Medtronic",
    "PANW": "Palo Alto Networks",
    "ANET": "Arista Networks",
    "MU": "Micron",
    "LRCX": "Lam Research",
    "ADI": "Analog Devices",
    "KLAC": "KLA",
    "DE": "Deere & Co. (John Deere)",
    "SBUX": "Starbucks",
    "GILD": "Gilead",
    "NKE": "Nike",
    "BMY": "Bristol-Myers Squibb",
    "MO": "Altria",
    "UPS": "UPS",
    "PLTR": "Palantir",
    "INTC": "Intel",
    "CRWD": "CrowdStrike",
    "PYPL": "PayPal",
    "ABNB": "Airbnb",
    "COIN": "Coinbase",
}

NASDAQ = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet (Google)",
    "META": "Meta Platforms (Facebook)",
    "AVGO": "Broadcom",
    "TSLA": "Tesla",
    "COST": "Costco",
    "NFLX": "Netflix",
    "AMD": "AMD",
    "PEP": "PepsiCo",
    "ADBE": "Adobe",
    "CSCO": "Cisco",
    "TMUS": "T-Mobile US",
    "QCOM": "Qualcomm",
    "INTU": "Intuit",
    "TXN": "Texas Instruments",
    "AMGN": "Amgen",
    "ISRG": "Intuitive Surgical",
    "BKNG": "Booking Holdings",
    "AMAT": "Applied Materials",
    "HON": "Honeywell",
    "CMCSA": "Comcast",
    "VRTX": "Vertex Pharmaceuticals",
    "ADP": "ADP",
    "PANW": "Palo Alto Networks",
    "GILD": "Gilead",
    "SBUX": "Starbucks",
    "MU": "Micron",
    "LRCX": "Lam Research",
    "ADI": "Analog Devices",
    "MELI": "MercadoLibre",
    "KLAC": "KLA",
    "REGN": "Regeneron",
    "MDLZ": "Mondelez",
    "INTC": "Intel",
    "PYPL": "PayPal",
    "SNPS": "Synopsys",
    "CDNS": "Cadence Design",
    "CRWD": "CrowdStrike",
    "MAR": "Marriott",
    "ORLY": "O'Reilly Automotive",
    "CTAS": "Cintas",
    "CEG": "Constellation Energy",
    "MRVL": "Marvell",
    "ABNB": "Airbnb",
    "FTNT": "Fortinet",
    "DASH": "DoorDash",
    "WDAY": "Workday",
    "ADSK": "Autodesk",
    "PCAR": "Paccar",
    "CPRT": "Copart",
    "MNST": "Monster Beverage",
    "PAYX": "Paychex",
    "ROST": "Ross Stores",
    "KDP": "Keurig Dr Pepper",
    "FAST": "Fastenal",
    "DDOG": "Datadog",
    "EA": "Electronic Arts",
    "KHC": "Kraft Heinz",
    "CTSH": "Cognizant",
    "TTWO": "Take-Two Interactive",
    "IDXX": "IDEXX Laboratories",
    "LULU": "Lululemon",
    "ZS": "Zscaler",
    "TEAM": "Atlassian",
    "DXCM": "Dexcom",
    "BIIB": "Biogen",
    "ON": "ON Semiconductor",
    "MCHP": "Microchip Technology",
    "WBD": "Warner Bros. Discovery",
    "ARM": "Arm Holdings",
    "PLTR": "Palantir",
    "APP": "AppLovin",
    "AXON": "Axon Enterprise",
    "MSTR": "Strategy (MicroStrategy)",
    "TTD": "The Trade Desk",
    "SHOP": "Shopify",
    "PDD": "PDD Holdings (Temu)",
}

CHINA = {
    "0700.HK": "Tencent",
    "9988.HK": "Alibaba",
    "1211.HK": "BYD",
    "1810.HK": "Xiaomi",
    "3690.HK": "Meituan",
    "9618.HK": "JD.com",
    "9888.HK": "Baidu",
    "PDD": "PDD Holdings (Temu)",
    "NIO": "NIO",
    "2015.HK": "Li Auto",
    "9868.HK": "XPeng",
    "9999.HK": "NetEase",
    "1024.HK": "Kuaishou",
    "9626.HK": "Bilibili",
    "9961.HK": "Trip.com",
    "2020.HK": "Anta Sports",
    "2331.HK": "Li Ning",
    "0175.HK": "Geely Automobile",
    "2333.HK": "Great Wall Motor",
    "0941.HK": "China Mobile",
    "0762.HK": "China Unicom",
    "0728.HK": "China Telecom",
    "0883.HK": "CNOOC",
    "0857.HK": "PetroChina",
    "0386.HK": "Sinopec",
    "1088.HK": "China Shenhua Energy",
    "2899.HK": "Zijin Mining",
    "0981.HK": "SMIC",
    "0992.HK": "Lenovo",
    "2382.HK": "Sunny Optical",
    "0285.HK": "BYD Electronic",
    "6690.HK": "Haier Smart Home",
    "9633.HK": "Nongfu Spring",
    "2319.HK": "China Mengniu Dairy",
    "0322.HK": "Tingyi (Master Kong)",
    "0151.HK": "Want Want China",
    "2269.HK": "WuXi Biologics",
    "1093.HK": "CSPC Pharmaceutical",
    "6862.HK": "Haidilao",
    "2318.HK": "Ping An Insurance",
    "1398.HK": "ICBC",
    "0939.HK": "China Construction Bank",
    "1299.HK": "AIA Group",
    "0388.HK": "Hong Kong Exchanges (HKEX)",
    "0168.HK": "Tsingtao Brewery",
    "0291.HK": "China Resources Beer",
    "1876.HK": "Budweiser APAC",
    "0027.HK": "Galaxy Entertainment",
    "1928.HK": "Sands China",
}

POPULAR = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet (Google)",
    "META": "Meta Platforms (Facebook)",
    "TSLA": "Tesla",
    "NFLX": "Netflix",
    "PLTR": "Palantir",
    "AMD": "AMD",
    "KO": "Coca-Cola",
    "MCD": "McDonald's",
    "NKE": "Nike",
    "V": "Visa",
    "COST": "Costco",
    "LLY": "Eli Lilly",
    "JPM": "JPMorgan Chase",
    "0700.HK": "Tencent",
    "9988.HK": "Alibaba",
    "1211.HK": "BYD",
    "1810.HK": "Xiaomi",
    "NIO": "NIO",
    "PDD": "PDD Holdings (Temu)",
    "NOVO-B.CO": "Novo Nordisk",
    "ASML.AS": "ASML",
    "MC.PA": "LVMH",
    "NESN.SW": "Nestlé",
    "SAP.DE": "SAP",
    "SIE.DE": "Siemens",
    "ALV.DE": "Allianz",
    "RHM.DE": "Rheinmetall",
    "IFX.DE": "Infineon",
    "ADS.DE": "adidas",
    "MBG.DE": "Mercedes-Benz",
    "BMW.DE": "BMW",
    "DTE.DE": "Deutsche Telekom",
    "ZAL.DE": "Zalando",
    "ABI.BR": "Anheuser-Busch InBev",
    "PM": "Philip Morris",
}

USA = {**US_TOP, **{t: n for t, n in NASDAQ.items() if t not in US_TOP}}
EU = {**DAX, **{t: n for t, n in MDAX.items() if t not in DAX}, **{t: n for t, n in EUROPE.items() if t not in DAX}}

UNIVERSES: dict[str, dict] = {
    "Beliebt": {"benchmark": "URTH", "benchmark_name": "MSCI World", "tickers": POPULAR},
    "USA": {"benchmark": "^GSPC", "benchmark_name": "S&P 500", "tickers": USA},
    "Europa": {"benchmark": "^STOXX50E", "benchmark_name": "Euro Stoxx 50", "tickers": EU},
    "China": {"benchmark": "^HSI", "benchmark_name": "Hang Seng", "tickers": CHINA},
    "Alle Märkte": {"benchmark": "URTH", "benchmark_name": "MSCI World", "tickers": {**USA, **EU, **CHINA}},
}
UNIVERSE_ICON = {"Beliebt": "🔥", "USA": "🇺🇸", "Europa": "🇪🇺", "China": "🇨🇳", "Alle Märkte": "🌍"}

BENCHMARKS: dict[str, str] = {
    "URTH": "MSCI World",
    "^GSPC": "S&P 500",
    "^NDX": "NASDAQ 100",
    "^STOXX50E": "Euro Stoxx 50",
    "^GDAXI": "DAX",
    "^HSI": "Hang Seng",
}

# Every stock from all lists: ticker -> name.
CATALOG: dict[str, str] = {}
for _universe in UNIVERSES.values():
    for _ticker, _name in _universe["tickers"].items():
        CATALOG.setdefault(_ticker, _name)

MARKET: dict[str, str] = {**{t: "US" for t in USA}, **{t: "EU" for t in EU}, **{t: "CN" for t in CHINA}}
MARKET_NAME = {"US": "USA", "EU": "Europa", "CN": "China"}

_SUFFIX_FLAG = {
    "DE": "🇩🇪", "F": "🇩🇪", "PA": "🇫🇷", "AS": "🇳🇱", "MI": "🇮🇹", "MC": "🇪🇸", "BR": "🇧🇪", "HE": "🇫🇮",
    "SW": "🇨🇭", "L": "🇬🇧", "CO": "🇩🇰", "ST": "🇸🇪", "OL": "🇳🇴", "VI": "🇦🇹", "LS": "🇵🇹", "IR": "🇮🇪",
    "HK": "🇨🇳", "SS": "🇨🇳", "SZ": "🇨🇳", "T": "🇯🇵", "TO": "🇨🇦", "AX": "🇦🇺",
}


def market_of(ticker: str) -> str:
    """US, EU or CN (unknown tickers are guessed from the exchange suffix)."""
    if ticker in MARKET:
        return MARKET[ticker]
    suffix = ticker.rsplit(".", 1)[1].upper() if "." in ticker else ""
    if suffix in ("HK", "SS", "SZ"):
        return "CN"
    if suffix and suffix not in ("T", "TO", "AX"):
        return "EU"
    return "US"


def flag(ticker: str) -> str:
    """Country flag of the listing (Chinese companies: 🇨🇳)."""
    if MARKET.get(ticker) == "CN":
        return "🇨🇳"
    suffix = ticker.rsplit(".", 1)[1].upper() if "." in ticker else ""
    return _SUFFIX_FLAG.get(suffix, "🇺🇸" if not suffix else "🌐")


# Other names people commonly search for.
ALIASES: dict[str, str] = {
    "google": "GOOGL",
    "youtube": "GOOGL",
    "facebook": "META",
    "instagram": "META",
    "whatsapp": "META",
    "daimler": "MBG.DE",
    "mercedes": "MBG.DE",
    "vw": "VOW3.DE",
    "telekom": "DTE.DE",
    "post": "DHL.DE",
    "munich re": "MUV2.DE",
    "microstrategy": "MSTR",
    "temu": "PDD",
    "pinduoduo": "PDD",
    "zara": "ITX.MC",
    "raytheon": "RTX",
    "john deere": "DE",
    "wechat": "0700.HK",
    "aliexpress": "9988.HK",
    "taobao": "9988.HK",
}


def _normalize(text: str) -> str:
    text = text.casefold().replace("ß", "ss")
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).strip()


def search_catalog(query: str, limit: int = 10) -> list[tuple[str, str]]:
    """Find stocks by name, ticker or common alias, best matches first."""
    q = _normalize(query)
    if not q:
        return []
    scored: dict[str, int] = {}
    for ticker, name in CATALOG.items():
        t, n = _normalize(ticker), _normalize(name)
        base = t.split(".")[0]
        if q in (t, base):
            rank = 0
        elif n.startswith(q) or any(w.startswith(q) for w in n.replace("(", " ").split()):
            rank = 1
        elif q in n:
            rank = 2
        elif t.startswith(q):
            rank = 3
        else:
            continue
        scored[ticker] = min(rank, scored.get(ticker, rank))
    for alias, ticker in ALIASES.items():
        if alias == q or (alias.startswith(q) and len(q) >= 3):
            scored[ticker] = min(scored.get(ticker, 1), 1)
    ranked = sorted(scored, key=lambda t: (scored[t], CATALOG[t].casefold()))
    return [(t, CATALOG[t]) for t in ranked[:limit]]
