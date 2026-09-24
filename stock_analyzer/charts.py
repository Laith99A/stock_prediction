"""Plotly figures for the Streamlit app."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import indicators as ind
from .backtest import StrategyResult
from .chart_reader import ChartReading, crossings, pivots
from .chart_school import example
from .formatting import fmt_date, fmt_price
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
from .ui import BASE_COLOR

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
    horizon_label = {BUY: "Verkauf ab ca.", HOLD: "Halten bis ca.", SELL: "Neubewertung ca."}[rec.side]
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
    if rec.side == HOLD:
        level(rec.upper_trigger, pal["muted"], "Kaufsignal", "dot")
        level(rec.lower_trigger, pal["muted"], "Verkaufssignal", "dot")
    elif rec.side == BUY:
        level(rec.lower_trigger, pal["muted"], "Signalende", "dot")
    elif rec.side == SELL:
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
    zones = [
        ("STRONG_BUY", STRONG_BUY_THRESHOLD, 100, "Stark kaufen", 0.12),
        ("BUY", BUY_THRESHOLD, STRONG_BUY_THRESHOLD, "Kaufen", 0.08),
        ("HOLD", SELL_THRESHOLD, BUY_THRESHOLD, "Halten", 0.06),
        ("SELL", STRONG_SELL_THRESHOLD, SELL_THRESHOLD, "Verkaufen", 0.08),
        ("STRONG_SELL", -100, STRONG_SELL_THRESHOLD, "Stark verkaufen", 0.12),
    ]
    for label, lo, hi, text, opacity in zones:
        fig.add_hrect(y0=lo, y1=hi, fillcolor=BASE_COLOR[label], opacity=opacity, line_width=0)
        fig.add_annotation(x=1.005, xref="paper", y=(lo + hi) / 2, xanchor="left", showarrow=False, text=text,
                           font=dict(color=pal["text"], size=11))
    for y in (STRONG_BUY_THRESHOLD, BUY_THRESHOLD, SELL_THRESHOLD, STRONG_SELL_THRESHOLD):
        fig.add_hline(y=y, line=dict(color=pal["muted"], width=1, dash="dash"))
    fig.add_trace(go.Scatter(x=data.index, y=data, name="Signal-Score", line=dict(color=pal["series"][0], width=2),
                             hovertemplate="%{y:.0f}", showlegend=False))
    _base_layout(fig, pal, 320)
    fig.update_layout(margin=dict(l=8, r=110, t=16, b=8))
    fig.update_yaxes(range=[-100, 100], title=None, tickvals=[-100, -55, -25, 0, 25, 55, 100])
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


# ---------------------------------------------------------------------------- chart reader & indicators

def _lines(fig: go.Figure, close: pd.Series, pal: dict, row: int | None = None, averages: bool = True) -> None:
    s1, s2, s3 = pal["series"]
    kw = {"row": row, "col": 1} if row else {}
    fig.add_trace(go.Scatter(x=close.index, y=close, name="Kurs", line=dict(color=s1, width=2),
                             hovertemplate="%{y:,.2f}"), **kw)
    if averages:
        for window, color, name in ((50, s2, "50-Tage-Linie"), (200, s3, "200-Tage-Linie")):
            line = ind.sma(close, window)
            if line.notna().any():
                fig.add_trace(go.Scatter(x=line.index, y=line, name=name, line=dict(color=color, width=2),
                                         hovertemplate="%{y:,.2f}"), **kw)


def reading_chart(df: pd.DataFrame, reading: ChartReading, pal: dict, months: int = 9) -> go.Figure:
    """Price with support/resistance and the numbered signs from the chart reader."""
    close = df["Close"]
    start = close.index[-1] - pd.DateOffset(months=months)
    fig = go.Figure()
    _lines(fig, close, pal)
    for level, color, text in ((reading.support, pal["good"], "Unterstützung"),
                               (reading.resistance, pal["critical"], "Widerstand")):
        if level is not None:
            fig.add_hline(y=level, line=dict(color=color, width=2, dash="dot"))
            fig.add_annotation(x=1, xref="paper", y=level, xanchor="left", showarrow=False,
                               text=f" {text} {level:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                               font=dict(color=pal["text"], size=12))
    for number, sign in enumerate(reading.signs, 1):
        if sign.date is None or sign.date < start:
            continue
        color = {1: pal["good"], -1: pal["critical"]}.get(sign.direction, pal["muted"])
        fig.add_trace(go.Scatter(
            x=[sign.date], y=[sign.price], mode="markers+text", text=[str(number)], textposition="middle center",
            textfont=dict(color="#ffffff", size=11), marker=dict(size=22, color=color, line=dict(color=pal["surface"],
                                                                                             width=2)),
            name=f"Zeichen {number}", showlegend=False, hovertemplate=f"{number}. {sign.text}<extra></extra>"))
    visible = close.loc[start:]
    levels = [lvl for lvl in (reading.support, reading.resistance) if lvl is not None]
    lo, hi = min([visible.min(), *levels]), max([visible.max(), *levels])
    pad = (hi - lo) * 0.06
    _base_layout(fig, pal, 420)
    fig.update_layout(margin=dict(l=8, r=150, t=40, b=8))
    fig.update_xaxes(range=[start, close.index[-1] + pd.offsets.BDay(3)])
    fig.update_yaxes(range=[lo - pad, hi + pad])
    return fig


def _volume_bars(fig: go.Figure, close: pd.Series, volume: pd.Series, pal: dict, row: int) -> None:
    up = close.diff().fillna(0) >= 0
    colors = np.where(up, pal["good"], pal["critical"])
    fig.add_trace(go.Bar(x=volume.index, y=volume, marker=dict(color=colors, opacity=0.6, line=dict(width=0)),
                         name="Volumen", showlegend=False, hovertemplate="%{y:,.0f}<extra>Volumen</extra>"),
                  row=row, col=1)


def _rsi_panel(fig: go.Figure, close: pd.Series, pal: dict, row: int) -> None:
    rsi = ind.rsi(close)
    # The trace must exist before the shapes: plotly skips shapes on empty subplots.
    fig.add_trace(go.Scatter(x=rsi.index, y=rsi, name="RSI", line=dict(color=pal["series"][0], width=2),
                             showlegend=False, hovertemplate="RSI %{y:.0f}<extra></extra>"), row=row, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor=pal["critical"], opacity=0.1, line_width=0, layer="below", row=row, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor=pal["good"], opacity=0.1, line_width=0, layer="below", row=row, col=1)
    for y in (30, 70):
        fig.add_hline(y=y, line=dict(color=pal["muted"], width=1, dash="dash"), row=row, col=1)
    fig.update_yaxes(range=[0, 100], tickvals=[0, 30, 50, 70, 100], row=row, col=1)


def _macd_panel(fig: go.Figure, close: pd.Series, pal: dict, row: int) -> None:
    macd = ind.macd(close)
    hist_colors = np.where(macd["hist"].fillna(0) >= 0, pal["good"], pal["critical"])
    fig.add_trace(go.Bar(x=macd.index, y=macd["hist"], marker=dict(color=hist_colors, opacity=0.5, line=dict(width=0)),
                         name="Abstand", showlegend=False, hovertemplate="%{y:.2f}<extra>Abstand</extra>"),
                  row=row, col=1)
    fig.add_trace(go.Scatter(x=macd.index, y=macd["macd"], name="MACD-Linie",
                             line=dict(color=pal["series"][0], width=2), hovertemplate="%{y:.2f}"), row=row, col=1)
    fig.add_trace(go.Scatter(x=macd.index, y=macd["signal"], name="Signallinie",
                             line=dict(color=pal["series"][1], width=2), hovertemplate="%{y:.2f}"), row=row, col=1)


def indicator_chart(df: pd.DataFrame, pal: dict, months: int = 12) -> go.Figure:
    """Volume, RSI and MACD for one stock as three stacked panels (shared time axis)."""
    start = df.index[-1] - pd.DateOffset(months=months)
    warm = df.loc[start - pd.DateOffset(months=3):]  # indicator warm-up before the visible window
    close = warm["Close"]
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.09, row_heights=[0.28, 0.36, 0.36],
                        subplot_titles=("Volumen (grün = Tag mit Gewinn, rot = mit Verlust)",
                                        "RSI – über 70 überkauft, unter 30 überverkauft",
                                        "MACD – blaue Linie über orange = Schwung nach oben"))
    _volume_bars(fig, close, warm["Volume"], pal, 1)
    _rsi_panel(fig, close, pal, 2)
    _macd_panel(fig, close, pal, 3)
    _base_layout(fig, pal, 620)
    fig.update_layout(margin=dict(l=8, r=8, t=40, b=8), legend=dict(y=-0.08, yanchor="top"))
    fig.update_xaxes(range=[start, df.index[-1]])
    fig.update_annotations(font=dict(size=12, color=pal["text"]), x=0, xanchor="left")
    return fig


# ---------------------------------------------------------------------------- chart school

def _marker(fig, x, y, text, color, pal, row=None, ay=-34):
    kw = {"row": row, "col": 1} if row else {}
    fig.add_annotation(x=x, y=y, text=text, showarrow=True, arrowhead=2, arrowcolor=color, ax=0, ay=ay,
                       font=dict(color=pal["text"], size=12), bgcolor=pal["surface"], bordercolor=color,
                       borderwidth=1, borderpad=3, **kw)


def lesson_chart(key: str, pal: dict) -> go.Figure | None:
    data = example(key)
    if not data:
        return None
    good, bad, muted = pal["good"], pal["critical"], pal["muted"]

    if key == "trend":
        fig = make_subplots(rows=1, cols=3, subplot_titles=list(data), horizontal_spacing=0.06)
        for col, (name, close) in enumerate(data.items(), 1):
            fig.add_trace(go.Scatter(x=close.index, y=close, line=dict(color=pal["series"][0], width=2),
                                     showlegend=False, hovertemplate="%{y:.1f}<extra></extra>"), row=1, col=col)
            for kind, color, symbol in (("high", good if col == 1 else bad if col == 3 else muted, "triangle-down"),
                                        ("low", good if col == 1 else bad if col == 3 else muted, "triangle-up")):
                pts = pivots(close, 7, kind)
                fig.add_trace(go.Scatter(x=pts.index, y=pts, mode="lines+markers", showlegend=False,
                                         line=dict(color=color, width=1.5, dash="dot"),
                                         marker=dict(size=9, color=color, symbol=symbol),
                                         hovertemplate=("Hoch" if kind == "high" else "Tief") + " %{y:.1f}<extra></extra>"),
                              row=1, col=col)
            fig.update_xaxes(showticklabels=False, row=1, col=col)
        _base_layout(fig, pal, 300)
        fig.update_annotations(font=dict(size=13, color=pal["text"]))
        return fig

    close = data["close"]
    if key in ("volumen", "rsi", "macd"):
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.58, 0.42])
        _lines(fig, close, pal, row=1, averages=False)
        if key == "volumen":
            _volume_bars(fig, close, data["volume"], pal, 2)
            peak = data["volume"].idxmax()
            _marker(fig, peak, float(data["volume"].max()), "hohes Volumen beim Ausbruch", good, pal, row=2, ay=-10)
            _marker(fig, peak, float(close.loc[peak]), "Ausbruch", good, pal, row=1)
        elif key == "rsi":
            _rsi_panel(fig, close, pal, 2)
            rsi = ind.rsi(close)
            _marker(fig, rsi.idxmax(), float(rsi.max()), "überkauft → Pause", bad, pal, row=2, ay=24)
            _marker(fig, rsi.idxmin(), float(rsi.min()), "überverkauft → Erholung", good, pal, row=2, ay=-24)
        else:
            _macd_panel(fig, close, pal, 2)
            macd = ind.macd(close)
            for date, direction in crossings(macd["macd"], macd["signal"])[1:]:
                if (date - close.index[0]).days < 60:
                    continue
                _marker(fig, date, float(close.loc[date]), "▲ Kaufsignal" if direction > 0 else "▼ Verkaufssignal",
                        good if direction > 0 else bad, pal, row=1, ay=-30 if direction > 0 else 30)
        _base_layout(fig, pal, 420)
        return fig

    fig = go.Figure()
    _lines(fig, close, pal, averages=key == "durchschnitte")
    if key == "grundlagen":
        for kind, color, ay, text in (("high", bad, -30, "Hoch"), ("low", good, 30, "Tief")):
            for date, price in pivots(close, 10, kind).items():
                _marker(fig, date, float(price), text, color, pal, ay=ay)
        _marker(fig, close.index[-1], float(close.iloc[-1]), "heute", pal["series"][0], pal)
        fig.update_xaxes(title_text="Zeit →")
        fig.update_yaxes(title_text="Kurs in €")
        fig.update_layout(showlegend=False)
    elif key == "durchschnitte":
        for date, direction in crossings(ind.sma(close, 50), ind.sma(close, 200)):
            price = float(ind.sma(close, 50).loc[date])
            _marker(fig, date, price, "Golden Cross" if direction > 0 else "Death Cross",
                    good if direction > 0 else bad, pal, ay=-40 if direction > 0 else 40)
        fig.update_xaxes(range=[close.index[200], close.index[-1]])
    elif key == "unterstuetzung":
        for level, color, text in ((95.5, good, "Unterstützung (Boden)"), (104.8, bad, "Widerstand (Decke)")):
            fig.add_hline(y=level, line=dict(color=color, width=2, dash="dot"))
            fig.add_annotation(x=close.index[5], y=level, text=text, showarrow=False, yshift=10 if level > 100 else -10,
                               xanchor="left", font=dict(color=pal["text"], size=12))
        breakout = close[close > 106].index[0]
        _marker(fig, breakout, float(close.loc[breakout]), "Ausbruch ↑", good, pal, ay=-40)
    _base_layout(fig, pal, 340)
    return fig
