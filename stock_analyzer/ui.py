"""HTML/CSS building blocks for the Streamlit app (badges, score meter, cards, tooltips)."""
from __future__ import annotations

from html import escape

from .formatting import LABEL_DE, fmt_date, fmt_days, fmt_pct, fmt_price, fmt_score
from .glossary import TERMS
from .recommendation import Recommendation
from .scoring import (
    BUY,
    BUY_THRESHOLD,
    HOLD,
    LABELS,
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

_LIGHT = """
  --card-bg:#ffffff; --card-bd:#e3e8ef; --muted:#5b6474; --soft:#f1f4f9;
  --shadow:0 1px 2px rgba(16,24,40,.05),0 2px 8px rgba(16,24,40,.06);
  --tip-bg:#0f172a; --tip-fg:#f8fafc; --up:#15803d; --down:#c62828;
  --sb-bg:#0e7a3a; --sb-fg:#ffffff; --sb-bd:#0e7a3a;
  --b-bg:rgba(31,157,85,.13); --b-fg:#11643a; --b-bd:rgba(31,157,85,.45);
  --h-bg:rgba(232,163,23,.17); --h-fg:#7a5200; --h-bd:rgba(232,163,23,.6);
  --s-bg:rgba(224,96,42,.13); --s-fg:#9a3412; --s-bd:rgba(224,96,42,.5);
  --ss-bg:#c62828; --ss-fg:#ffffff; --ss-bd:#c62828;
"""
_DARK = """
  --card-bg:#111a2b; --card-bd:#243049; --muted:#9aa6bd; --soft:#162238;
  --shadow:none;
  --tip-bg:#f1f5f9; --tip-fg:#0f172a; --up:#4ade80; --down:#f87171;
  --sb-bg:#12924a; --sb-fg:#ffffff; --sb-bd:#12924a;
  --b-bg:rgba(34,197,94,.14); --b-fg:#6ee7a1; --b-bd:rgba(34,197,94,.45);
  --h-bg:rgba(245,180,40,.15); --h-fg:#fcd34d; --h-bd:rgba(245,180,40,.5);
  --s-bg:rgba(249,115,22,.15); --s-fg:#fdba74; --s-bd:rgba(249,115,22,.5);
  --ss-bg:#d32f2f; --ss-fg:#ffffff; --ss-bd:#d32f2f;
"""

_CSS = """
.block-container { padding-top: 1.6rem; padding-bottom: 4rem; max-width: 1360px; }
.stTabs [data-baseweb="tab"] p { font-size: 1.02rem; font-weight: 600; }
div[data-testid="stMetric"] { background: var(--card-bg); box-shadow: var(--shadow); }
div[data-testid="stMetricValue"] { font-weight: 700; }

.hero { position: relative; overflow: hidden; border-radius: 22px; padding: 28px 32px; margin-bottom: 14px;
  color: #fff; background: linear-gradient(120deg, #0b2447 0%, #173d7a 45%, #1f6feb 100%);
  display: flex; justify-content: space-between; align-items: flex-end; gap: 20px; flex-wrap: wrap; }
.hero::before { content: ""; position: absolute; right: -80px; top: -120px; width: 380px; height: 380px;
  border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,.16), rgba(255,255,255,0) 70%); }
.hero .kicker { font-size: .78rem; letter-spacing: .14em; text-transform: uppercase; opacity: .8; font-weight: 700; }
.hero .title { font-size: 2.15rem; font-weight: 800; line-height: 1.15; margin: 6px 0 8px; }
.hero .sub { opacity: .9; max-width: 680px; font-size: 1.02rem; line-height: 1.45; }
.hero .chips { display: flex; gap: 8px; flex-wrap: wrap; position: relative; }
.chip { background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.25); border-radius: 999px;
  padding: 5px 12px; font-size: .82rem; white-space: nowrap; }

.card { background: var(--card-bg); border: 1px solid var(--card-bd); border-radius: 16px; padding: 18px 20px;
  box-shadow: var(--shadow); }
.muted { color: var(--muted); }

.badge { display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; padding: 3px 12px;
  font-weight: 700; font-size: .84rem; border: 1px solid transparent; white-space: nowrap; line-height: 1.5; }
.badge.lg { font-size: 1.12rem; padding: 7px 18px; }
.badge .arrow { font-size: .75em; letter-spacing: -1px; }
""" + "\n".join(
    f".badge.{c} {{ background: var(--{c}-bg); color: var(--{c}-fg); border-color: var(--{c}-bd); }}"
    for c in CLS.values()
) + """

.tt { border-bottom: 1px dotted currentColor; cursor: help; position: relative; outline: none; }
.tt .tip { visibility: hidden; opacity: 0; position: absolute; left: 50%; bottom: calc(100% + 8px);
  transform: translateX(-50%); width: max-content; max-width: 280px; background: var(--tip-bg); color: var(--tip-fg);
  padding: 8px 11px; border-radius: 9px; font-size: .8rem; line-height: 1.4; font-weight: 400; z-index: 1000;
  transition: opacity .12s; white-space: normal; text-align: left; box-shadow: 0 8px 24px rgba(0,0,0,.22);
  pointer-events: none; }
.tt:hover .tip, .tt:focus .tip { visibility: visible; opacity: 1; }
.info { display: inline-flex; width: 16px; height: 16px; border-radius: 50%; align-items: center; justify-content: center;
  font-size: .68rem; font-weight: 700; border: 1px solid currentColor; opacity: .6; margin-left: 4px;
  border-bottom-style: solid; vertical-align: 1px; }

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

.dist { display: flex; gap: 3px; height: 36px; }
.dist .seg { display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 700;
  font-size: .9rem; min-width: 0; overflow: hidden; }
.dist .seg:first-child { border-radius: 10px 0 0 10px; }
.dist .seg:last-child { border-radius: 0 10px 10px 0; }
.dist .seg:only-child { border-radius: 10px; }
.dist .seg.h { color: #3d2a00; }
.dist-legend { display: flex; flex-wrap: wrap; gap: 6px 18px; margin-top: 12px; font-size: .88rem; }
.dist-legend .dot { width: 10px; height: 10px; border-radius: 3px; display: inline-block; margin-right: 6px; }

.scard { display: flex; flex-direction: column; gap: 6px; height: 100%; border-top-width: 4px; }
.scard .top { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.scard .name { font-weight: 750; font-size: 1.08rem; line-height: 1.25; margin-top: 4px; }
.scard .meta { color: var(--muted); font-size: .85rem; }
.scard .row { display: flex; justify-content: space-between; gap: 10px; font-size: .9rem; }
.scard .row span:first-child { color: var(--muted); }
.scard .score { font-weight: 800; font-size: 1.05rem; font-variant-numeric: tabular-nums; }

.dhead { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }
.dname { font-size: 1.75rem; font-weight: 800; line-height: 1.2; }
.dmeta { color: var(--muted); font-size: .92rem; margin-top: 2px; }
.dprice { font-size: 1.75rem; font-weight: 800; text-align: right; line-height: 1.2; }
.chg { font-size: .92rem; font-weight: 700; }
.chg.up { color: var(--up); } .chg.down { color: var(--down); }

.action { border-left-width: 6px; }
.action .headline { font-size: 1.3rem; font-weight: 800; margin-bottom: 4px; }
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

.sec { margin: 26px 0 10px; }
.sec .t { font-size: 1.28rem; font-weight: 800; }
.sec .s { color: var(--muted); font-size: .92rem; margin-top: 2px; }

.steps { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.step .n { display: inline-flex; width: 28px; height: 28px; border-radius: 50%; align-items: center; justify-content: center;
  background: #1f6feb; color: #fff; font-weight: 800; margin-bottom: 8px; }
.step .h { font-weight: 750; margin-bottom: 4px; }

.ggrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 12px; }
.gcard .gt { font-weight: 800; font-size: 1.05rem; }
.gcard .gs { font-weight: 600; margin: 4px 0 6px; }
.gcard .gl { color: var(--muted); line-height: 1.5; }
.gcard .ge { margin-top: 8px; font-size: .9rem; background: var(--soft); border-radius: 8px; padding: 6px 10px; }
"""


def css(theme_type: str | None) -> str:
    """Global stylesheet. Follows the Streamlit theme when known, else the OS setting."""
    if theme_type == "dark":
        variables = f":root {{{_DARK}}}"
    elif theme_type == "light":
        variables = f":root {{{_LIGHT}}}"
    else:
        variables = f":root {{{_LIGHT}}}\n@media (prefers-color-scheme: dark) {{ :root {{{_DARK}}} }}"
    return f"<style>{variables}\n{_CSS}</style>"


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


def hero(kicker: str, title: str, subtitle: str, chips: list[str]) -> str:
    chip_html = "".join(f'<span class="chip">{escape(c)}</span>' for c in chips)
    return (f'<div class="hero"><div><div class="kicker">{escape(kicker)}</div><div class="title">{escape(title)}</div>'
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


def distribution_bar(counts: dict[str, int]) -> str:
    total = sum(counts.values()) or 1
    segs, legend = [], []
    for label in LABELS:
        n = counts.get(label, 0)
        legend.append(f'<span><span class="dot" style="background:{BASE_COLOR[label]}"></span>'
                      f'{escape(LABEL_DE[label])} <b>{n}</b> <span class="muted">({n / total:.0%})</span></span>')
        if n:
            text = str(n) if n / total >= 0.05 else ""
            segs.append(f'<div class="seg {CLS[label]}" style="flex:{n};background:{BASE_COLOR[label]}" '
                        f'title="{escape(LABEL_DE[label])}: {n}">{text}</div>')
    return f'<div class="dist">{"".join(segs)}</div><div class="dist-legend">{"".join(legend)}</div>'


def date_caption(rec: Recommendation) -> str:
    return {BUY: "Verkauf ab ca.", HOLD: "Halten bis ca.", SELL: "Neubewertung ab"}[rec.side]


def stock_card(rec: Recommendation) -> str:
    rows = [f'<div class="row"><span>{date_caption(rec)}</span><b>{fmt_date(rec.horizon_date)}</b></div>']
    if rec.side == BUY:
        rows.append(f'<div class="row"><span>Kursziel</span><b>{fmt_price(rec.target_price, rec.currency)} '
                    f'({fmt_pct(rec.expected_return, 0)})</b></div>')
        rows.append(f'<div class="row"><span>Stop-Loss</span><b>{fmt_price(rec.stop_loss, rec.currency)}</b></div>')
    else:
        rows.append(f'<div class="row"><span>Signal aktiv seit</span><b>{rec.signal_age} Tagen</b></div>')
    return (f'<div class="card scard" style="border-top-color:{BASE_COLOR[rec.label]}">'
            f'<div class="top">{badge(rec.label)}<span class="score">{fmt_score(rec.score)}</span></div>'
            f'<div class="name">{escape(rec.name)}</div>'
            f'<div class="meta">{escape(rec.ticker)} · {fmt_price(rec.price, rec.currency)}</div>'
            f'{"".join(rows)}</div>')


def detail_header(rec: Recommendation, change_1d: float | None) -> str:
    chg = ""
    if change_1d is not None:
        cls = "up" if change_1d >= 0 else "down"
        chg = f'<div class="chg {cls}">{fmt_pct(change_1d)} zum Vortag</div>'
    return (f'<div class="card"><div class="dhead">'
            f'<div><div class="dname">{escape(rec.name)}</div>'
            f'<div class="dmeta">{term(rec.ticker, "ticker")} · Stand {fmt_date(rec.as_of)}</div></div>'
            f'<div>{badge(rec.label, large=True)}</div>'
            f'<div><div class="dprice">{fmt_price(rec.price, rec.currency)}</div>{chg}</div>'
            f'</div>{score_meter(rec.score, rec.label)}</div>')


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
