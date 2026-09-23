"""Plotly figures for the Streamlit app."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from . import indicators as ind
from .backtest import StrategyResult
from .formatting import fmt_date, fmt_price
from .recommendation import Recommendation
from .scoring import BUY, BUY_THRESHOLD, HOLD, SELL, SELL_THRESHOLD

SHORT_LABELS = {
    "trend": "Trend",
    "momentum": "Momentum",
    "rsi": "RSI",
    "high52": "52-Wochen-Hoch",
    "volume": "Volumen",
    "relative": "Relative Stärke",
    "market": "Marktumfeld",
}

# Validated categorical slots 1-3 plus diverging and status colours, per theme.
PALETTES = {
    "light": {
        "series": ["#2a78d6", "#eb6834", "#1baf7a"],
        "positive": "#2a78d6",
        "negative": "#e34948",
        "good": "#0ca30c",
        "critical": "#d03b3b",
        "muted": "#898781",
        "grid": "#e1e0d9",
        "baseline": "#c3c2b7",
        "text": "#52514e",
        "surface": "#fcfcfb",
    },
    "dark": {
        "series": ["#3987e5", "#d95926", "#199e70"],
        "positive": "#3987e5",
        "negative": "#e66767",
        "good": "#0ca30c",
        "critical": "#d03b3b",
        "muted": "#898781",
        "grid": "#2c2c2a",
        "baseline": "#383835",
        "text": "#c3c2b7",
        "surface": "#1a1a19",
    },
}


def _base_layout(fig: go.Figure, pal: dict, height: int, title: str | None = None) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=40 if title else 16, b=8),
        title=dict(text=title, font=dict(size=15)) if title else None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family='system-ui, -apple-system, "Segoe UI", sans-serif', color=pal["text"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0),
        hovermode="x unified",
        separators=",.",
    )
    fig.update_xaxes(showgrid=False, linecolor=pal["baseline"], ticks="outside", tickcolor=pal["baseline"])
    fig.update_yaxes(gridcolor=pal["grid"], gridwidth=1, zeroline=False)
    return fig


def price_chart(df: pd.DataFrame, rec: Recommendation, pal: dict, months: int = 12) -> go.Figure:
    close = df["Close"]
    sma50 = ind.sma(close, 50)
    sma200 = ind.sma(close, 200)
    s1, s2, s3 = pal["series"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=close.index, y=close, name="Kurs", line=dict(color=s1, width=2),
                             hovertemplate="%{y:,.2f}"))
    fig.add_trace(go.Scatter(x=sma50.index, y=sma50, name="50-Tage-Linie", line=dict(color=s2, width=2),
                             hovertemplate="%{y:,.2f}"))
    fig.add_trace(go.Scatter(x=sma200.index, y=sma200, name="200-Tage-Linie", line=dict(color=s3, width=2),
                             hovertemplate="%{y:,.2f}"))

    start = rec.as_of - pd.DateOffset(months=months)
    end = rec.horizon_date + pd.offsets.BDay(5)
    horizon_label = {BUY: "Verkauf ab ca.", HOLD: "Halten bis ca.", SELL: "Neubewertung ca."}[rec.label]
    fig.add_vline(x=rec.horizon_date, line=dict(color=pal["muted"], width=1.5, dash="dot"))
    fig.add_annotation(x=rec.horizon_date, y=1, yref="paper", yanchor="bottom", showarrow=False,
                       text=f"{horizon_label} {fmt_date(rec.horizon_date)}", font=dict(color=pal["text"], size=12))

    def level(price: float | None, color: str, text: str, dash: str = "dash") -> None:
        if price is None:
            return
        fig.add_shape(type="line", x0=rec.as_of, x1=rec.horizon_date, y0=price, y1=price,
                      line=dict(color=color, width=2, dash=dash))
        fig.add_annotation(x=rec.horizon_date, y=price, xanchor="left", showarrow=False,
                           text=f" {text} {fmt_price(price, rec.currency)}", font=dict(color=pal["text"], size=12))

    level(rec.target_price, pal["good"], "▲ Kursziel")
    level(rec.stop_loss, pal["critical"], "▼ Stop-Loss")
    if rec.label == HOLD:
        level(rec.upper_trigger, pal["muted"], "Kaufsignal", "dot")
        level(rec.lower_trigger, pal["muted"], "Verkaufssignal", "dot")
    elif rec.label == BUY:
        level(rec.lower_trigger, pal["muted"], "Signalende", "dot")
    elif rec.label == SELL:
        level(rec.upper_trigger, pal["muted"], "Signalende", "dot")

    fig.add_trace(go.Scatter(x=[rec.as_of], y=[rec.price], mode="markers", name="Aktuell",
                             marker=dict(size=9, color=s1, line=dict(color=pal["surface"], width=2)),
                             showlegend=False, hovertemplate="%{y:,.2f}"))

    visible = close.loc[start:]
    lows = [visible.min()] + [p for p in (rec.stop_loss, rec.lower_trigger) if p is not None]
    highs = [visible.max()] + [p for p in (rec.target_price, rec.upper_trigger) if p is not None]
    pad = (max(highs) - min(lows)) * 0.06
    _base_layout(fig, pal, 460)
    fig.update_layout(margin=dict(l=8, r=170, t=56, b=8))
    fig.update_xaxes(range=[start, end])
    fig.update_yaxes(range=[min(lows) - pad, max(highs) + pad], title=None)
    return fig


def score_chart(scores: pd.DataFrame, pal: dict, months: int = 24) -> go.Figure:
    data = scores["signal"].dropna()
    data = data.loc[data.index[-1] - pd.DateOffset(months=months):]
    fig = go.Figure()
    fig.add_hrect(y0=BUY_THRESHOLD, y1=100, fillcolor=pal["good"], opacity=0.08, line_width=0)
    fig.add_hrect(y0=-100, y1=SELL_THRESHOLD, fillcolor=pal["critical"], opacity=0.08, line_width=0)
    for y, text in ((BUY_THRESHOLD, "Kaufen ab +25"), (SELL_THRESHOLD, "Verkaufen ab −25")):
        fig.add_hline(y=y, line=dict(color=pal["muted"], width=1, dash="dash"))
        fig.add_annotation(x=1, xref="paper", y=y, xanchor="right", yanchor="bottom" if y > 0 else "top",
                           showarrow=False, text=text, font=dict(color=pal["text"], size=11),
                           bgcolor=pal["surface"], opacity=0.9)
    fig.add_trace(go.Scatter(x=data.index, y=data, name="Signal-Score", line=dict(color=pal["series"][0], width=2),
                             hovertemplate="%{y:.0f}", showlegend=False))
    _base_layout(fig, pal, 300)
    fig.update_yaxes(range=[-100, 100], title=None, tickvals=[-100, -50, -25, 0, 25, 50, 100])
    return fig


def component_chart(rec: Recommendation, pal: dict) -> go.Figure:
    items = [(SHORT_LABELS[k], v) for k, v in rec.components.items() if np.isfinite(v)]
    items.sort(key=lambda kv: kv[1])
    labels = [k for k, _ in items]
    values = [v * 100 for _, v in items]
    colors = [pal["positive"] if v >= 0 else pal["negative"] for v in values]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h", marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:+.0f}" for v in values], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:+.0f}<extra></extra>",
    ))
    _base_layout(fig, pal, 320)
    fig.update_layout(hovermode="closest", barcornerradius=4, bargap=0.35, margin=dict(l=8, r=36, t=16, b=8))
    fig.update_xaxes(range=[-135, 135], zeroline=True, zerolinecolor=pal["baseline"], zerolinewidth=1,
                     showgrid=True, gridcolor=pal["grid"], tickvals=[-100, -50, 0, 50, 100])
    fig.update_yaxes(showgrid=False)
    return fig


def equity_chart(result: StrategyResult, pal: dict) -> go.Figure:
    eq = result.equity
    s1, s2, _ = pal["series"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=eq.index, y=(eq["strategy"] - 1) * 100, name="Strategie (nur bei „Kaufen“ investiert)",
                             line=dict(color=s1, width=2), hovertemplate="%{y:+.1f} %"))
    fig.add_trace(go.Scatter(x=eq.index, y=(eq["buy_and_hold"] - 1) * 100, name="Kaufen und Liegenlassen",
                             line=dict(color=s2, width=2), hovertemplate="%{y:+.1f} %"))
    _base_layout(fig, pal, 320)
    fig.update_yaxes(ticksuffix=" %", title=None)
    return fig
