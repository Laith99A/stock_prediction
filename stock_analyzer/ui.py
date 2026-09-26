"""HTML/CSS building blocks for the Streamlit app (badges, score meter, cards, tooltips)."""
from __future__ import annotations

from html import escape

import pandas as pd

from .chart_reader import ChartReading
from .chart_school import CHECKLIST_DOWN, CHECKLIST_UP, Lesson
from .formatting import LABEL_DE, fmt_date, fmt_days, fmt_num, fmt_pct, fmt_price, fmt_score
from .fundamentals import GroupSummary, Metric
from .glossary import TERMS
from .halal import MAX_DEBT_TO_EQUITY, HalalCheck
from .recommendation import Recommendation
from .scoring import (
    BUY,
    BUY_THRESHOLD,
    HOLD,
    SELL,
    SELL_THRESHOLD,
    STRONG_BUY_THRESHOLD,
    STRONG_SELL_THRESHOLD,
)

CLS = {"STRONG_BUY": "sb", "BUY": "b", "HOLD": "h", "SELL": "s", "STRONG_SELL": "ss"}
ARROW = {"STRONG_BUY": "▲▲", "BUY": "▲", "HOLD": "●", "SELL": "▼", "STRONG_SELL": "▼▼"}
BASE_COLOR = {
    "STRONG_BUY": "#0e7a3a",
    "BUY": "#1f9d55",
    "HOLD": "#e8a317",
    "SELL": "#e0602a",
    "STRONG_SELL": "#c62828",
}

# Dark design: neutral charcoal surfaces, one deliberate jade accent (doubles as the halal signal).
_VARS = """
  --card-bg:#17181a; --card-bd:#26282b; --muted:#999da0; --soft:#1e2022; --text:#eef0f1;
  --shadow:0 1px 0 rgba(255,255,255,.02) inset, 0 10px 28px rgba(0,0,0,.45);
  --accent:#22c98f; --on-accent:#04140f; --accent-soft:rgba(34,201,143,.14);
  --tip-bg:#f1f5f9; --tip-fg:#0f172a; --up:#34d399; --down:#f87171;
  --sb-bg:#12924a; --sb-fg:#ffffff; --sb-bd:#12924a;
  --b-bg:rgba(34,197,94,.14); --b-fg:#6ee7a1; --b-bd:rgba(34,197,94,.45);
  --h-bg:rgba(245,180,40,.15); --h-fg:#fcd34d; --h-bd:rgba(245,180,40,.5);
  --s-bg:rgba(249,115,22,.15); --s-fg:#fdba74; --s-bd:rgba(249,115,22,.5);
  --ss-bg:#d32f2f; --ss-fg:#ffffff; --ss-bd:#d32f2f;
  --r-bg:rgba(248,113,113,.14); --r-fg:#fca5a5; --r-bd:rgba(248,113,113,.45);
  --i-bg:rgba(122,156,214,.14); --i-fg:#9db8e8; --i-bd:rgba(122,156,214,.42);
  --halal-bg:rgba(34,201,143,.16); --halal-fg:#7fe6bd; --halal-bd:rgba(34,201,143,.5);
"""

_CSS = """
.block-container { padding-top: 1.2rem; padding-bottom: 4rem; max-width: 1280px; }
h1, h2, h3, .sec .t, .hero .title, .dname, .sc-name, .wotd .w, .brand {
  font-family: "Twemoji Country Flags", "Space Grotesk", Inter, sans-serif; }

/* narrow sidebar with the market navigation */
section[data-testid="stSidebar"] { width: 236px !important; min-width: 236px !important; max-width: 236px !important; }
section[data-testid="stSidebar"] .block-container, section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding-left: .6rem; padding-right: .6rem; }
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .3rem; }
section[data-testid="stSidebar"] [data-testid="stButton"] button { justify-content: flex-start; padding: 6px 12px;
  min-height: 38px; border-radius: 12px; }
section[data-testid="stSidebar"] [data-testid="stButton"] button > div { justify-content: flex-start; width: 100%; }
section[data-testid="stSidebar"] [data-testid="stButton"] button p { text-align: left; font-weight: 600; }
section[data-testid="stSidebar"] button[kind="primary"] { background: var(--accent); border: none; }
section[data-testid="stSidebar"] button[kind="primary"] p { color: var(--on-accent); }
section[data-testid="stSidebar"] button[kind="tertiary"]:hover { background: var(--soft); }
.brand { font-size: 1.15rem; font-weight: 700; margin: 2px 0 0; }
.brand-sub { color: var(--muted); font-size: .8rem; margin-bottom: 12px; }
.navlabel { color: var(--muted); font-size: .72rem; letter-spacing: .12em; text-transform: uppercase; font-weight: 700;
  margin: 8px 0 0 4px; padding-bottom: 10px; line-height: 1.2; }

/* pill-shaped navigation tabs */
[data-testid="stTabs"] [role="tablist"] { gap: 8px; flex-wrap: wrap; border: none; box-shadow: none; padding-bottom: 6px; }
[data-testid="stTabs"] [role="tablist"]::after, [data-testid="stTabs"] [role="tablist"]::before { display: none; }
[data-testid="stTabs"] [data-testid="stTab"] { background: var(--card-bg); border: 1px solid var(--card-bd); border-radius: 999px;
  padding: 7px 18px; height: auto; transition: border-color .15s; }
[data-testid="stTabs"] [data-testid="stTab"]:hover { border-color: var(--accent); }
[data-testid="stTabs"] [data-testid="stTab"] > div:not([data-testid]) { display: none; }  /* underline indicator */
[data-testid="stTabs"] [data-testid="stTab"] p { font-size: .98rem; font-weight: 600; }
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] { background: var(--accent); border-color: transparent; }
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] p { color: var(--on-accent); }
div[data-testid="stMetric"] { background: var(--card-bg); box-shadow: var(--shadow); }
div[data-testid="stMetricValue"] { font-weight: 700; font-variant-numeric: tabular-nums; }
div[data-testid="stPopover"] button, .stButton button { border-radius: 12px; transition: transform .1s; }
div[data-testid="stPopover"] button:active, .stButton button:active,
section[data-testid="stSidebar"] [data-testid="stButton"] button:active { transform: scale(.97); }
@media (prefers-reduced-motion: reduce) {
  div[data-testid="stPopover"] button, .stButton button { transition: none; }
  div[data-testid="stPopover"] button:active, .stButton button:active,
  section[data-testid="stSidebar"] [data-testid="stButton"] button:active { transform: none; }
}

.hero { position: relative; overflow: hidden; border-radius: 24px; padding: 26px 30px; margin-bottom: 16px;
  color: var(--text); background: radial-gradient(circle at 12% 0%, var(--accent-soft), transparent 55%), var(--card-bg);
  border: 1px solid var(--card-bd); box-shadow: var(--shadow);
  display: flex; justify-content: space-between; align-items: flex-end; gap: 20px; flex-wrap: wrap; }
.hero .kicker { font-size: .78rem; letter-spacing: .16em; text-transform: uppercase; font-weight: 700; color: var(--accent); }
.hero .title { font-size: 2.2rem; font-weight: 700; letter-spacing: -.01em; line-height: 1.1; margin: 6px 0 8px;
  text-wrap: balance; }
.hero .title span { color: var(--accent); }
.hero .sub { color: var(--muted); max-width: 640px; font-size: 1rem; line-height: 1.45; text-wrap: pretty; }
.hero .chips { display: flex; gap: 8px; flex-wrap: wrap; position: relative; }
.chip { background: var(--soft); border: 1px solid var(--card-bd); border-radius: 999px; color: var(--muted);
  padding: 5px 12px; font-size: .82rem; white-space: nowrap; }

.card { background: var(--card-bg); border: 1px solid var(--card-bd); border-radius: 18px; padding: 18px 20px;
  box-shadow: var(--shadow); }
.muted { color: var(--muted); }
.up { color: var(--up); } .down { color: var(--down); }

.badge { display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; padding: 3px 12px;
  font-weight: 700; font-size: .84rem; border: 1px solid transparent; white-space: nowrap; line-height: 1.5; }
.badge.lg { font-size: 1.12rem; padding: 7px 18px; }
.badge .arrow { font-size: .75em; letter-spacing: -1px; }
""" + "\n".join(
    f".badge.{c} {{ background: var(--{c}-bg); color: var(--{c}-fg); border-color: var(--{c}-bd); }}"
    for c in CLS.values()
) + """

.hb { display: inline-flex; align-items: center; gap: 4px; border-radius: 999px; padding: 2px 9px; font-size: .76rem;
  font-weight: 700; border: 1px solid transparent; white-space: nowrap; }
.hb.halal { background: var(--halal-bg); color: var(--halal-fg); border-color: var(--halal-bd); }
.hb.nicht { background: var(--r-bg); color: var(--r-fg); border-color: var(--r-bd); }
.hb.pruefen { background: var(--h-bg); color: var(--h-fg); border-color: var(--h-bd); }
.hb.lg { font-size: .95rem; padding: 5px 14px; }

.tt { border-bottom: 1px dotted currentColor; cursor: help; position: relative; border-radius: 3px; }
.tt:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
.tt .tip { visibility: hidden; opacity: 0; position: absolute; left: 50%; bottom: calc(100% + 8px);
  transform: translateX(-50%); width: max-content; max-width: 280px; background: var(--tip-bg); color: var(--tip-fg);
  padding: 8px 11px; border-radius: 9px; font-size: .8rem; line-height: 1.4; font-weight: 400; z-index: 1000;
  transition: opacity .12s; white-space: normal; text-align: left; box-shadow: 0 8px 24px rgba(0,0,0,.35);
  pointer-events: none; font-family: Inter, sans-serif; }
.tt:hover .tip, .tt:focus .tip { visibility: visible; opacity: 1; }
.info { display: inline-flex; width: 16px; height: 16px; border-radius: 50%; align-items: center; justify-content: center;
  font-size: .68rem; font-weight: 700; border: 1px solid currentColor; opacity: .6; margin-left: 4px;
  border-bottom-style: solid; vertical-align: 1px; }

.pulse { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 6px; }
.pulse .card { padding: 14px 16px; }
.pulse .k { font-size: .8rem; color: var(--muted); margin-bottom: 4px; }
.pulse .v { font-size: 1.25rem; font-weight: 750; }
.pulse .s { font-size: .82rem; color: var(--muted); margin-top: 2px; }
.wotd { border-left: 4px solid var(--accent); }
.wotd .w { font-size: 1.1rem; font-weight: 700; }

.sc { display: flex; flex-direction: column; gap: 8px; padding: 16px 16px 14px; height: 100%; transition: border-color .15s; }
.sc:hover { border-color: var(--accent); }
.sc-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.sc-name { font-weight: 700; font-size: 1.08rem; line-height: 1.2; }
.sc-meta { color: var(--muted); font-size: .8rem; margin-top: 2px; }
.sc-mid { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.sc-price { font-size: 1.45rem; font-weight: 800; line-height: 1.1; font-variant-numeric: tabular-nums; }
.sc-sub { color: var(--muted); font-size: .8rem; margin-top: 2px; }
.sc-bottom { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.sc-score { font-weight: 800; font-variant-numeric: tabular-nums; }
.sc-line { font-size: .84rem; color: var(--muted); border-top: 1px solid var(--card-bd); padding-top: 8px; }
.sc-about { font-size: .82rem; color: var(--muted); line-height: 1.4; min-height: 2.8em; display: -webkit-box;
  -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

.company .ct { font-size: 1.15rem; font-weight: 800; margin-bottom: 6px; }
.company .cd { font-size: 1.02rem; line-height: 1.55; margin-bottom: 12px; }
.facts { display: flex; flex-wrap: wrap; gap: 8px; }
.fact { display: inline-flex; flex-direction: column; background: var(--soft); border-radius: 12px; padding: 7px 12px;
  font-size: .9rem; min-width: 110px; }
.fact .k { color: var(--muted); font-size: .72rem; text-transform: uppercase; letter-spacing: .06em; }
a.fact { color: var(--text); text-decoration: none; justify-content: center; }
a.fact:hover, a.fact:focus-visible { outline: 1px solid var(--accent); }
.sc-line b { color: var(--text); }

.meter { position: relative; margin: 34px 4px 4px; }
.meter-track { display: flex; gap: 3px; height: 14px; }
.meter-zone { height: 100%; border-radius: 4px; opacity: .25; }
.meter-zone.active { opacity: 1; }
.meter-marker { position: absolute; top: -6px; width: 4px; height: 26px; border-radius: 2px; background: currentColor;
  transform: translateX(-50%); box-shadow: 0 0 0 2px var(--card-bg); }
.meter-value { position: absolute; top: -32px; transform: translateX(-50%); font-weight: 800; font-size: 1rem;
  white-space: nowrap; }
.meter-labels { display: flex; gap: 3px; margin-top: 8px; font-size: .76rem; color: var(--muted); }
.meter-labels div { text-align: center; line-height: 1.2; }
.meter-labels .active { color: inherit; font-weight: 700; }

.dhead { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }
.dname { font-size: 1.8rem; font-weight: 700; letter-spacing: -.01em; line-height: 1.2; }
.dmeta { color: var(--muted); font-size: .92rem; margin-top: 4px; display: flex; gap: 8px; align-items: center;
  flex-wrap: wrap; }
.dprice { font-size: 1.8rem; font-weight: 800; text-align: right; line-height: 1.2; font-variant-numeric: tabular-nums; }
.chg { font-size: .9rem; font-weight: 700; text-align: right; }
.chg.up { color: var(--up); } .chg.down { color: var(--down); }

.hcard { border-left-width: 6px; }
.hcard.halal { border-left-color: var(--accent); } .hcard.nicht { border-left-color: #ef4444; }
.hcard.pruefen { border-left-color: #f59e0b; }
.hcard .hh { display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 10px; }
.hcard .ht { font-size: 1.15rem; font-weight: 800; }
.hcard ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
.hcard li { display: flex; gap: 10px; align-items: flex-start; background: var(--soft); border-radius: 12px;
  padding: 9px 12px; line-height: 1.4; }

.action { border-left-width: 6px; }
.action .headline { font-size: 1.25rem; font-weight: 800; margin-bottom: 4px; }
.action .summary { color: var(--muted); margin-bottom: 12px; }
.plan { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.plan li { display: flex; gap: 12px; align-items: flex-start; background: var(--soft); border-radius: 12px;
  padding: 10px 14px; line-height: 1.45; }
.plan .ico { font-size: 1.2rem; line-height: 1.3; }

.reasons { list-style: none; padding: 0; margin: 0; }
.reasons li { display: flex; gap: 10px; align-items: flex-start; padding: 9px 0; border-bottom: 1px solid var(--card-bd);
  line-height: 1.4; }
.reasons li:last-child { border-bottom: none; }
.reasons .ico { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: .75rem; font-weight: 800; flex-shrink: 0; margin-top: 1px; }
.reasons .pos { background: var(--b-bg); color: var(--b-fg); }
.reasons .neg { background: var(--s-bg); color: var(--s-fg); }
.reasons .neu { background: var(--soft); color: var(--muted); }

.sec { margin: 24px 0 10px; }
.sec .t { font-size: 1.3rem; font-weight: 700; letter-spacing: -.01em; }
.sec .s { color: var(--muted); font-size: .92rem; margin-top: 2px; }

.steps { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.step .n { display: inline-flex; width: 28px; height: 28px; border-radius: 50%; align-items: center; justify-content: center;
  background: var(--accent); color: var(--on-accent); font-weight: 800; margin-bottom: 8px; }
.step .h { font-weight: 750; margin-bottom: 4px; }

.ggrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 12px; }
.gcard .gt { font-weight: 800; font-size: 1.05rem; }
.gcard .gs { font-weight: 600; margin: 4px 0 6px; }
.gcard .gl { color: var(--muted); line-height: 1.5; }
.gcard .ge { margin-top: 8px; font-size: .9rem; background: var(--soft); border-radius: 8px; padding: 6px 10px; }

.pill { display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; padding: 2px 10px; font-weight: 650;
  font-size: .8rem; border: 1px solid transparent; white-space: nowrap; }
.pill.p-good { background: var(--b-bg); color: var(--b-fg); border-color: var(--b-bd); }
.pill.p-ok { background: var(--h-bg); color: var(--h-fg); border-color: var(--h-bd); }
.pill.p-bad { background: var(--r-bg); color: var(--r-fg); border-color: var(--r-bd); }
.pill.p-info { background: var(--i-bg); color: var(--i-fg); border-color: var(--i-bd); }
.pill.p-na { background: var(--soft); color: var(--muted); }
.fsum { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 14px; }
.fsum .g { font-size: .85rem; color: var(--muted); margin-bottom: 6px; }
.mgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 12px; }
.mcard { display: flex; flex-direction: column; gap: 6px; padding: 14px 16px; }
.mcard.hl { grid-column: span 2; border-width: 2px; }
.mcard .mt { font-size: .86rem; color: var(--muted); font-weight: 600; }
.mcard .mv { font-size: 1.55rem; font-weight: 800; line-height: 1.15; font-variant-numeric: tabular-nums; }
.mcard .mr { font-size: .78rem; color: var(--muted); line-height: 1.35; }
.gauge { position: relative; margin: 22px 0 18px; }
.gauge .track { display: flex; gap: 3px; height: 10px; }
.gauge .track div { border-radius: 4px; opacity: .8; }
.gauge .mark { position: absolute; top: -5px; width: 4px; height: 20px; border-radius: 2px; background: currentColor;
  transform: translateX(-50%); box-shadow: 0 0 0 2px var(--card-bg); }
.gauge .limit { position: absolute; top: -18px; height: 34px; border-left: 2px dashed var(--accent); }
.gauge .limit span { position: absolute; top: -2px; left: 6px; font-size: .7rem; color: var(--halal-fg); white-space: nowrap; }
.gauge .ticks { position: relative; height: 14px; font-size: .72rem; color: var(--muted); margin-top: 4px; }
.gauge .ticks span { position: absolute; transform: translateX(-50%); }
.tally { display: flex; height: 12px; border-radius: 6px; overflow: hidden; gap: 3px; margin: 8px 0 4px; }
.signs { list-style: none; padding: 0; margin: 0; }
.signs li { display: flex; gap: 12px; align-items: flex-start; padding: 9px 0; border-bottom: 1px solid var(--card-bd);
  line-height: 1.45; }
.signs li:last-child { border-bottom: none; }
.signs .num { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: .78rem; font-weight: 800; flex-shrink: 0; color: #fff; }
.signs .dir { font-weight: 800; margin-right: 4px; }
.lesson .intro { font-size: 1.02rem; margin: 2px 0 12px; line-height: 1.5; }
.lesson ul { margin: 0 0 6px 0; padding-left: 20px; line-height: 1.55; }
.updown { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; margin-top: 10px; }
.updown > div { border-radius: 12px; padding: 12px 14px; }
.updown .u { background: var(--b-bg); border: 1px solid var(--b-bd); }
.updown .d { background: var(--r-bg); border: 1px solid var(--r-bd); }
.updown .h { font-weight: 800; margin-bottom: 6px; }
.updown ul { margin: 0; padding-left: 18px; line-height: 1.5; }
"""


def css() -> str:
    """Global stylesheet (the app always uses its dark theme)."""
    return f"<style>:root {{{_VARS}}}\n{_CSS}</style>"


def term(text: str, key: str) -> str:
    """Text with a hover/tap explanation from the glossary."""
    tip = escape(TERMS[key].short)
    return f'<span class="tt" tabindex="0">{escape(text)}<span class="tip">{tip}</span></span>'


def info(key: str) -> str:
    """Small ⓘ icon with a glossary tooltip."""
    tip = escape(TERMS[key].short)
    return f'<span class="tt info" tabindex="0">i<span class="tip">{tip}</span></span>'


def badge(label: str, large: bool = False) -> str:
    size = " lg" if large else ""
    return (f'<span class="badge {CLS[label]}{size}"><span class="arrow">{ARROW[label]}</span>'
            f"{escape(LABEL_DE[label])}</span>")


def hero(kicker: str, title_html: str, subtitle: str, chips: list[str]) -> str:
    """Header banner. `title_html` is static markup; wrap a word in <span> to highlight it."""
    chip_html = "".join(f'<span class="chip">{escape(c)}</span>' for c in chips)
    return (f'<div class="hero"><div><div class="kicker">{escape(kicker)}</div><div class="title">{title_html}</div>'
            f'<div class="sub">{subtitle}</div></div><div class="chips">{chip_html}</div></div>')


def section(title: str, subtitle: str = "") -> str:
    sub = f'<div class="s">{subtitle}</div>' if subtitle else ""
    return f'<div class="sec"><div class="t">{title}</div>{sub}</div>'


# Zone widths on the -100..+100 scale.
_ZONES = [
    ("STRONG_SELL", -100, STRONG_SELL_THRESHOLD),
    ("SELL", STRONG_SELL_THRESHOLD, SELL_THRESHOLD),
    ("HOLD", SELL_THRESHOLD, BUY_THRESHOLD),
    ("BUY", BUY_THRESHOLD, STRONG_BUY_THRESHOLD),
    ("STRONG_BUY", STRONG_BUY_THRESHOLD, 100),
]


def score_meter(score: float, label: str) -> str:
    zones, labels = [], []
    for zone_label, lo, hi in _ZONES:
        width = (hi - lo) / 2
        active = " active" if zone_label == label else ""
        zones.append(f'<div class="meter-zone{active}" style="flex:{width};background:{BASE_COLOR[zone_label]}"></div>')
        labels.append(f'<div class="{active.strip()}" style="flex:{width}">{escape(LABEL_DE[zone_label])}</div>')
    pos = min(max((score + 100) / 2, 1.0), 99.0)
    return (f'<div class="meter"><div class="meter-value" style="left:{pos}%">{fmt_score(score)}</div>'
            f'<div class="meter-track">{"".join(zones)}</div>'
            f'<div class="meter-marker" style="left:{pos}%"></div>'
            f'<div class="meter-labels">{"".join(labels)}</div></div>')


def date_caption(rec: Recommendation) -> str:
    return {BUY: "Verkauf ab ca.", HOLD: "Halten bis ca.", SELL: "Neubewertung ab"}[rec.side]


def halal_badge(check: HalalCheck, large: bool = False) -> str:
    size = " lg" if large else ""
    text = {"halal": "☪ Halal", "nicht": "✕ Nicht halal", "pruefen": "? Prüfen"}[check.status]
    tip = escape(" · ".join(check.reasons) or "Geschäftsfeld und Verschuldung erfüllen die Kriterien")
    return f'<span class="hb {check.status}{size}" title="{tip}">{text}</span>'


def sparkline(close: pd.Series, days: int = 63, width: int = 120, height: int = 38) -> str:
    """Tiny SVG line of the last ~3 months (green if up, red if down)."""
    values = close.dropna().iloc[-days:].to_numpy(dtype=float)
    if len(values) < 2:
        return ""
    lo, hi = float(values.min()), float(values.max())
    span = hi - lo or 1.0
    xs = [i * width / (len(values) - 1) for i in range(len(values))]
    ys = [height - 3 - (v - lo) / span * (height - 6) for v in values]
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    color = "#34d399" if values[-1] >= values[0] else "#f87171"
    area = f"0,{height} {points} {width},{height}"
    return (f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" aria-hidden="true">'
            f'<polygon points="{area}" fill="{color}" opacity=".12"></polygon>'
            f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" '
            f'stroke-linecap="round"></polyline></svg>')


def stock_tile(rec: Recommendation, check: HalalCheck, flag_emoji: str, price_eur: float | None,
               change_1d: float | None, sector: str, close: pd.Series, description: str = "") -> str:
    """Card for the discovery grid."""
    local = "" if rec.currency == "EUR" else fmt_price(rec.price, rec.currency)
    chg = ""
    if change_1d is not None:
        chg = f'<span class="{"up" if change_1d >= 0 else "down"}">{fmt_pct(change_1d)}</span>'
    sub = " · ".join(x for x in (local, chg) if x)
    meta = " · ".join(x for x in (escape(rec.ticker), escape(sector)) if x)
    price = fmt_price(price_eur, "EUR") if price_eur is not None else fmt_price(rec.price, rec.currency)
    return (f'<div class="card sc">'
            f'<div class="sc-top"><div><div class="sc-name">{flag_emoji} {escape(rec.name)}</div>'
            f'<div class="sc-meta">{meta}</div></div>{halal_badge(check)}</div>'
            f'<div class="sc-about">{escape(description)}</div>'
            f'<div class="sc-mid"><div><div class="sc-price">{price}</div><div class="sc-sub">{sub}</div></div>'
            f'{sparkline(close)}</div>'
            f'<div class="sc-bottom">{badge(rec.label)}<span class="sc-score">Score {fmt_score(rec.score)}</span></div>'
            f'<div class="sc-line">📅 {date_caption(rec)} <b>{fmt_date(rec.horizon_date)}</b></div></div>')


def detail_header(rec: Recommendation, change_1d: float | None, check: HalalCheck | None = None,
                  flag_emoji: str = "", price_eur: float | None = None) -> str:
    chg = ""
    if change_1d is not None:
        cls = "up" if change_1d >= 0 else "down"
        chg = f'<div class="chg {cls}">{fmt_pct(change_1d)} zum Vortag</div>'
    local = ""
    if price_eur is not None and rec.currency != "EUR":
        local = f'<div class="chg muted">{fmt_price(rec.price, rec.currency)}</div>'
    price = fmt_price(price_eur, "EUR") if price_eur is not None else fmt_price(rec.price, rec.currency)
    halal = halal_badge(check, large=True) if check else ""
    return (f'<div class="card"><div class="dhead">'
            f'<div><div class="dname">{flag_emoji} {escape(rec.name)}</div>'
            f'<div class="dmeta">{term(rec.ticker, "ticker")} · Stand {fmt_date(rec.as_of)} {halal}</div></div>'
            f'<div>{badge(rec.label, large=True)}</div>'
            f'<div><div class="dprice">{price}</div>{local}{chg}</div>'
            f'</div>{score_meter(rec.score, rec.label)}</div>')


def big_number(value: float | None) -> str:
    """1.2e12 -> "1,2 Bio." (German short scale)."""
    if value is None:
        return "–"
    for unit, size in (("Bio.", 1e12), ("Mrd.", 1e9), ("Mio.", 1e6)):
        if abs(value) >= size:
            return f"{fmt_num(value / size, 1)} {unit}"
    return fmt_num(value, 0)


def company_card(name: str, description: str, german: bool, facts: list[tuple[str, str]],
                 website: str | None = None) -> str:
    """"About the company" card: short description plus key facts."""
    items = "".join(f'<span class="fact"><span class="k">{escape(k)}</span><b>{escape(v)}</b></span>'
                    for k, v in facts if v)
    if website and website.startswith(("http://", "https://")):
        items += f'<a class="fact" href="{escape(website)}" target="_blank" rel="noopener">🌐 Website</a>'
    note = ""
    if description and not german:
        note = '<div class="muted" style="font-size:.8rem;margin-top:8px">Beschreibung von Yahoo Finance (Englisch).</div>'
    text = escape(description) if description else "Für dieses Unternehmen liegt keine Beschreibung vor."
    return (f'<div class="card company"><div class="ct">🏢 Über {escape(name)}</div><div class="cd">{text}</div>'
            f'<div class="facts">{items}</div>{note}</div>')


def halal_card(check: HalalCheck) -> str:
    rows = [
        ("Geschäftsfeld", check.business_status, check.business_reason),
        ("Verschuldung", check.debt_status, check.debt_reason),
    ]
    icon = {"halal": "✅", "nicht": "❌", "pruefen": "❔"}
    items = "".join(f"<li><span>{icon[st]}</span><span><b>{name}:</b> {escape(text)}</span></li>"
                    for name, st, text in rows)
    head = {"halal": "Halal-konform", "nicht": "Nicht halal", "pruefen": "Bitte selbst prüfen"}[check.status]
    return (f'<div class="card hcard {check.status}"><div class="hh"><div class="ht">☪️ Halal-Check: {head}</div>'
            f'{halal_badge(check)}</div><ul>{items}</ul>'
            f'<div class="muted" style="font-size:.8rem;margin-top:10px">Vereinfachte Prüfung: Geschäftsfeld + '
            f'{term("Schuldengrenze 33 %", "halal_schulden")}. Ersetzt keine vollständige Shariah-Prüfung.</div></div>')


def pulse(items: list[tuple[str, str, str]], extra: str = "") -> str:
    """Row of small status cards (label, value, caption); `extra` is appended as another card."""
    cards = "".join(f'<div class="card"><div class="k">{k}</div><div class="v">{v}</div><div class="s">{sub}</div></div>'
                    for k, v, sub in items)
    return f'<div class="pulse">{cards}{extra}</div>'


def word_card(key: str) -> str:
    t = TERMS[key]
    return (f'<div class="card wotd"><div class="k muted" style="font-size:.8rem">💡 Begriff des Tages</div>'
            f'<div class="w">{escape(t.title)}</div><div class="muted" style="font-size:.86rem;margin-top:4px">'
            f'{escape(t.short)}</div></div>')


def _trigger(rec: Recommendation, price: float | None, above: bool, outcome: str) -> str:
    if price is None:
        reach = fmt_pct(8 * rec.atr / rec.price, 0, sign=False)
        return f"{outcome}: derzeit außer Reichweite (dafür wäre eine Kursbewegung von über {reach} nötig)."
    if abs(price / rec.price - 1) < 0.002:
        return f"{outcome}: steht auf der Kippe – schon bei unverändertem Kurs in den nächsten Tagen möglich."
    move, verb = ("über", "steigt") if above else ("unter", "fällt")
    return (f"{outcome}, wenn der Kurs innerhalb einer Woche {move} "
            f"<b>{fmt_price(price, rec.currency)}</b> ({fmt_pct(price / rec.price - 1)}) {verb}.")


_HEADLINE = {
    "STRONG_BUY": "Stark kaufen – sehr positives Gesamtbild",
    "BUY": "Kaufen – positives Gesamtbild",
    "HOLD": "Halten – kein klares Signal, abwarten",
    "SELL": "Verkaufen – negatives Gesamtbild",
    "STRONG_SELL": "Stark verkaufen – sehr negatives Gesamtbild",
}


def action_box(rec: Recommendation) -> str:
    comps = [v for v in rec.components.values() if v == v]
    pos = sum(v > 0.1 for v in comps)
    neg = sum(v < -0.1 for v in comps)
    summary = (f"{pos} von {len(comps)} {term('Faktoren', 'score')} sprechen dafür, {neg} dagegen "
               f"(Score {fmt_score(rec.score)}).")
    cur = rec.currency
    plan: list[tuple[str, str]] = []
    if rec.side == BUY:
        plan += [
            ("📅", f"<b>Verkauf empfohlen ab ca. {fmt_date(rec.horizon_date)}</b> ({fmt_days(rec.horizon_days)}) – "
                   f"dann läuft das Signal voraussichtlich aus."),
            ("🎯", f"<b>Früher verkaufen</b>, sobald das {term('Kursziel', 'kursziel')} "
                   f"<b>{fmt_price(rec.target_price, cur)}</b> ({fmt_pct(rec.expected_return)}) erreicht ist."),
            ("🛑", f"<b>Sofort verkaufen</b>, falls der Kurs unter den {term('Stop-Loss', 'stop_loss')} "
                   f"<b>{fmt_price(rec.stop_loss, cur)}</b> ({fmt_pct(rec.stop_loss / rec.price - 1)}) fällt."),
            ("⚠️", _trigger(rec, rec.lower_trigger, False, "Frühwarnung – das Kaufsignal endet")),
        ]
    elif rec.side == HOLD:
        lean = {"steigend": "Der Score steigt – es geht eher Richtung <b>Kaufen</b>.",
                "fallend": "Der Score fällt – es geht eher Richtung <b>Verkaufen</b>.",
                "seitwärts": "Der Score bewegt sich seitwärts."}[rec.tendency]
        plan += [
            ("📅", f"<b>Halten bis ca. {fmt_date(rec.horizon_date)}</b> ({fmt_days(rec.horizon_days)}), dann neu bewerten."),
            ("🟢", _trigger(rec, rec.upper_trigger, True, "Kaufsignal")),
            ("🔴", _trigger(rec, rec.lower_trigger, False, "Verkaufssignal")),
            ("🧭", f"{term('Tendenz', 'tendenz')}: {lean}"),
        ]
    else:
        plan += [
            ("🚪", "<b>Verkaufen bzw. nicht einsteigen.</b>"),
            ("📅", f"Neubewertung frühestens ca. <b>{fmt_date(rec.horizon_date)}</b> ({fmt_days(rec.horizon_days)})."),
            ("🔁", _trigger(rec, rec.upper_trigger, True, "Das Verkaufssignal endet")),
        ]
    items = "".join(f'<li><span class="ico">{ico}</span><span>{text}</span></li>' for ico, text in plan)
    return (f'<div class="card action" style="border-left-color:{BASE_COLOR[rec.label]}">'
            f'<div class="headline">{escape(_HEADLINE[rec.label])}</div>'
            f'<div class="summary">{summary}</div><ul class="plan">{items}</ul>'
            f'<div class="muted" style="margin-top:10px;font-size:.82rem">Zeithorizont geschätzt aus: '
            f'{escape(rec.horizon_basis)}.</div></div>')


# Glossary key for each explanation line produced by recommendation._reasons.
_REASON_TERMS = [
    ("200-Tage-Linie", "gleitender_durchschnitt"),
    ("50-Tage-Linie", "gleitender_durchschnitt"),
    ("Cross", "golden_cross"),
    ("Performance", "performance"),
    ("MACD", "macd"),
    ("RSI", "rsi"),
    ("52-Wochen-Hoch", "hoch_52w"),
    ("Volumen", "volumen"),
    ("Umsatz", "volumen"),
    ("Markt (3", "relative_staerke"),
    ("Marktumfeld", "marktumfeld"),
]


def reasons_list(reasons: list[tuple[str, int]]) -> str:
    icons = {1: ("pos", "✓"), 0: ("neu", "–"), -1: ("neg", "!")}
    items = []
    for text, sentiment in reasons:
        cls, sym = icons[sentiment]
        key = next((k for needle, k in _REASON_TERMS if needle in text), None)
        body = escape(text) + (info(key) if key else "")
        items.append(f'<li><span class="ico {cls}">{sym}</span><span>{body}</span></li>')
    return f'<div class="card"><ul class="reasons">{"".join(items)}</ul></div>'


def glossary_grid(keys: list[str]) -> str:
    return f'<div class="ggrid">{"".join(glossary_card(k) for k in keys)}</div>'


def glossary_card(key: str) -> str:
    t = TERMS[key]
    example = f'<div class="ge">💡 Beispiel: {escape(t.example)}</div>' if t.example else ""
    return (f'<div class="card gcard"><div class="gt">{escape(t.title)}</div><div class="gs">{escape(t.short)}</div>'
            f'<div class="gl">{escape(t.long)}</div>{example}</div>')


def steps(items: list[tuple[str, str]]) -> str:
    cards = "".join(f'<div class="card step"><div class="n">{i}</div><div class="h">{escape(h)}</div>'
                    f'<div class="muted">{body}</div></div>' for i, (h, body) in enumerate(items, 1))
    return f'<div class="steps">{cards}</div>'


# ---------------------------------------------------------------------------- key figures

STATUS_ICON = {"good": "●", "ok": "●", "bad": "●", "info": "ℹ", "na": "–"}


def pill(status: str, text: str) -> str:
    return f'<span class="pill p-{status}">{STATUS_ICON[status]} {escape(text)}</span>'


def de_gauge(value: float | None) -> str:
    """Scale 0 … 3 for debt-to-equity with green / amber / red zones."""
    if value is None:
        return ""
    zones = [("#1f9d55", 1.0), ("#e8a317", 1.0), ("#c62828", 1.0)]
    track = "".join(f'<div style="flex:{w};background:{c}"></div>' for c, w in zones)
    pos = min(max(value, 0.0), 3.0) / 3.0 * 100
    ticks = "".join(f'<span style="left:{v / 3 * 100}%">{fmt_num(v, 0) if v % 1 == 0 else fmt_num(v, 1)}'
                    f'{"+" if v == 3 else ""}</span>' for v in (0, 1, 2, 3))
    limit = MAX_DEBT_TO_EQUITY / 3.0 * 100
    return (f'<div class="gauge"><div class="limit" style="left:{limit}%"><span>Halal-Grenze 0,33</span></div>'
            f'<div class="track">{track}</div><div class="mark" style="left:{pos}%"></div>'
            f'<div class="ticks">{ticks}</div></div>')


def metric_card(metric: Metric) -> str:
    extra = de_gauge(metric.value) if metric.key == "verschuldungsgrad" and metric.status != "info" else ""
    cls = " hl" if metric.highlight else ""
    return (f'<div class="card mcard{cls}"><div class="mt">{escape(metric.title)}{info(metric.key)}</div>'
            f'<div class="mv">{escape(metric.text)}</div>{extra}<div>{pill(metric.status, metric.verdict)}</div>'
            f'<div class="mr">Faustregel: {escape(metric.rule)}</div></div>')


def fundamentals_summary(summaries: list[GroupSummary]) -> str:
    cards = "".join(f'<div class="card"><div class="g">{escape(g.group)}</div>'
                    f'<div>{pill(g.status, g.verdict)}</div></div>' for g in summaries)
    return f'<div class="fsum">{cards}</div>'


def metric_grid(metrics: list[Metric]) -> str:
    return f'<div class="mgrid">{"".join(metric_card(m) for m in metrics)}</div>'


# ---------------------------------------------------------------------------- chart reading & school

_DIR = {1: ("#1f9d55", "▲"), -1: ("#c62828", "▼"), 0: ("#8a93a3", "•")}


def reading_summary(reading: ChartReading) -> str:
    up, down = reading.bullish, reading.bearish
    neutral = len(reading.signs) - up - down
    bar = "".join(f'<div style="flex:{n};background:{c}"></div>' for n, c in
                  ((up, "#1f9d55"), (neutral, "#b8bec9"), (down, "#c62828")) if n)
    return (f'<div class="card"><div style="font-size:1.15rem;font-weight:800">{escape(reading.verdict)}</div>'
            f'<div class="tally">{bar}</div>'
            f'<div class="muted"><b style="color:#1f9d55">▲ {up}</b> Zeichen für steigende Kurse · '
            f'<b style="color:#c62828">▼ {down}</b> für fallende · {neutral} neutral · '
            f'Trend: <b>{escape(reading.trend)}</b></div></div>')


def reading_list(reading: ChartReading, lesson_titles: dict[str, str]) -> str:
    items = []
    for number, sign in enumerate(reading.signs, 1):
        color, arrow = _DIR[sign.direction]
        lesson = lesson_titles.get(sign.lesson, "")
        hint = f'<div class="muted" style="font-size:.8rem">📚 Lektion: {escape(lesson)}</div>' if lesson else ""
        items.append(f'<li><span class="num" style="background:{color}">{number}</span><div>'
                     f'<span class="dir" style="color:{color}">{arrow}</span>{escape(sign.text)}{hint}</div></li>')
    return f'<div class="card"><ul class="signs">{"".join(items)}</ul></div>'


def lesson_card(lesson: Lesson) -> str:
    how = "".join(f"<li>{item}</li>" for item in lesson.how)  # trusted static text (may contain <b>)
    updown = ""
    if lesson.up or lesson.down:
        up = "".join(f"<li>{escape(x)}</li>" for x in lesson.up)
        down = "".join(f"<li>{escape(x)}</li>" for x in lesson.down)
        updown = (f'<div class="updown"><div class="u"><div class="h">▲ Zeichen für steigende Kurse</div><ul>{up}</ul>'
                  f'</div><div class="d"><div class="h">▼ Zeichen für fallende Kurse</div><ul>{down}</ul></div></div>')
    return (f'<div class="card lesson"><div class="intro">{escape(lesson.intro)}</div>'
            f'<div style="font-weight:750;margin-bottom:4px">So liest du es</div><ul>{how}</ul>{updown}</div>')


def checklist() -> str:
    up = "".join(f"<li>{escape(x)}</li>" for x in CHECKLIST_UP)
    down = "".join(f"<li>{escape(x)}</li>" for x in CHECKLIST_DOWN)
    return (f'<div class="updown"><div class="u"><div class="h">▲ Spricht für steigende Kurse</div><ul>{up}</ul></div>'
            f'<div class="d"><div class="h">▼ Spricht für fallende Kurse</div><ul>{down}</ul></div></div>')
