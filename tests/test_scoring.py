import numpy as np
import pandas as pd

from stock_analyzer.scoring import (
    BUY,
    BUY_THRESHOLD,
    HOLD,
    SELL,
    classify,
    compute_scores,
    price_for_threshold,
    signal_after_path,
)


def test_classify_thresholds():
    assert classify(25) == BUY
    assert classify(24.9) == HOLD
    assert classify(-25) == SELL
    assert classify(float("nan")) is None


def test_trends_are_classified(uptrend, downtrend, sideways):
    assert compute_scores(uptrend)["label"].iloc[-1] == BUY
    assert compute_scores(downtrend)["label"].iloc[-1] == SELL
    assert compute_scores(sideways)["label"].iloc[-1] == HOLD


def test_score_range_and_benchmark(uptrend, downtrend):
    scores = compute_scores(uptrend, benchmark=downtrend["Close"])
    valid = scores["raw"].dropna()
    assert valid.between(-100, 100).all()
    # Beating a falling market counts positively, the falling market itself negatively.
    assert scores["relative"].iloc[-1] > 0.5
    assert scores["market"].iloc[-1] < -0.5


def test_missing_benchmark_renormalises(uptrend):
    scores = compute_scores(uptrend)
    assert scores[["relative", "market"]].iloc[-1].isna().all()
    assert np.isfinite(scores["signal"].iloc[-1])


def test_price_trigger_is_consistent(sideways):
    atr_step = float(sideways["Close"].iloc[-1]) * 0.01
    up = price_for_threshold(sideways, None, BUY_THRESHOLD, "up", atr_step)
    assert up is not None and up > sideways["Close"].iloc[-1]
    base = sideways.iloc[-320:]
    assert signal_after_path(base, None, up) >= BUY_THRESHOLD
    assert signal_after_path(base, None, up * 0.97) < BUY_THRESHOLD


def test_trigger_unreachable_returns_none(downtrend):
    close = float(downtrend["Close"].iloc[-1])
    assert price_for_threshold(downtrend, None, 90, "up", close * 0.001, max_steps=3) is None


def test_scores_index_matches_input(uptrend):
    scores = compute_scores(uptrend)
    pd.testing.assert_index_equal(scores.index, uptrend.index)
