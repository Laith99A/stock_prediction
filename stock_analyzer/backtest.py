"""Historical check of the signals (in-sample, for plausibility only)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .scoring import BUY, LABELS, SIDE


def signal_quality(scores: pd.DataFrame, close: pd.Series, horizon: int = 21) -> pd.DataFrame:
    """Average return over the next `horizon` trading days after each signal type."""
    forward = close.shift(-horizon) / close - 1.0
    data = pd.DataFrame({"label": scores["label"], "fwd": forward}).dropna()
    rows = []
    for label in LABELS:
        fwd = data.loc[data["label"] == label, "fwd"]
        rows.append(
            {
                "label": label,
                "days": len(fwd),
                "mean": fwd.mean() if len(fwd) else np.nan,
                "median": fwd.median() if len(fwd) else np.nan,
                "hit_rate": (fwd > 0).mean() if len(fwd) else np.nan,
            }
        )
    fwd = data["fwd"]
    rows.append(
        {
            "label": "ALL",
            "days": len(fwd),
            "mean": fwd.mean() if len(fwd) else np.nan,
            "median": fwd.median() if len(fwd) else np.nan,
            "hit_rate": (fwd > 0).mean() if len(fwd) else np.nan,
        }
    )
    return pd.DataFrame(rows).set_index("label")


@dataclass
class StrategyResult:
    equity: pd.DataFrame  # columns: strategy, buy_and_hold (both start at 1.0)
    strategy_return: float
    buy_and_hold_return: float
    strategy_max_drawdown: float
    buy_and_hold_max_drawdown: float
    time_in_market: float
    trades: int


def _max_drawdown(equity: pd.Series) -> float:
    return float((equity / equity.cummax() - 1.0).min())


def strategy_performance(scores: pd.DataFrame, close: pd.Series) -> StrategyResult:
    """Invested while the signal is on the buy side (Buy or Strong Buy, entry/exit
    at the close), else in cash."""
    sides = scores["side"] if "side" in scores else scores["label"].map(SIDE)
    valid = sides.notna()
    close = close[valid]
    in_market = (sides[valid] == BUY).astype(float)
    next_return = close.pct_change().shift(-1).fillna(0.0)
    strategy = (1.0 + next_return * in_market).cumprod().shift(1).fillna(1.0)
    buy_hold = (close / close.iloc[0]).rename("buy_and_hold")
    equity = pd.DataFrame({"strategy": strategy, "buy_and_hold": buy_hold})
    trades = int(((in_market.diff() == 1).sum()) + (1 if in_market.iloc[0] == 1 else 0))
    return StrategyResult(
        equity=equity,
        strategy_return=float(strategy.iloc[-1] - 1.0),
        buy_and_hold_return=float(buy_hold.iloc[-1] - 1.0),
        strategy_max_drawdown=_max_drawdown(strategy),
        buy_and_hold_max_drawdown=_max_drawdown(buy_hold),
        time_in_market=float(in_market.mean()),
        trades=trades,
    )
