import pandas as pd
import pytest

from stock_analyzer.recommendation import (
    HORIZON_LIMITS,
    InsufficientDataError,
    analyze,
    days_to_threshold,
    empirical_remaining,
)
from stock_analyzer.scoring import BUY, HOLD, SELL


def test_buy_has_target_stop_and_sell_date(uptrend):
    rec = analyze(uptrend, "UP", currency="EUR")
    assert rec.label == BUY
    assert rec.target_price > rec.price > rec.stop_loss > 0
    assert rec.target_price - rec.price >= 3 * rec.atr - 1e-9
    lo, hi = HORIZON_LIMITS[BUY]
    assert lo <= rec.horizon_days <= hi
    assert rec.horizon_date > rec.as_of
    assert rec.lower_trigger is None or rec.lower_trigger <= rec.price
    assert rec.upper_trigger is None


def test_sell_has_no_target(downtrend):
    rec = analyze(downtrend, "DOWN")
    assert rec.label == SELL
    assert rec.target_price is None and rec.stop_loss is None
    assert rec.upper_trigger is None or rec.upper_trigger >= rec.price


def test_hold_has_horizon_and_triggers(sideways):
    rec = analyze(sideways, "FLAT")
    assert rec.label == HOLD
    lo, hi = HORIZON_LIMITS[HOLD]
    assert lo <= rec.horizon_days <= hi
    assert rec.target_price is None
    assert rec.upper_trigger is not None and rec.upper_trigger > rec.price
    assert rec.lower_trigger is None or rec.lower_trigger < rec.price
    assert rec.reasons


def test_short_history_raises(uptrend):
    with pytest.raises(InsufficientDataError):
        analyze(uptrend.iloc[:50], "SHORT")


def test_empirical_remaining_uses_completed_longer_runs():
    # first run (cut off) and last run (ongoing, age 3) are excluded.
    labels = pd.Series(
        [BUY] * 50 + [HOLD] * 5 + [BUY] * 10 + [HOLD] * 5 + [BUY] * 20 + [HOLD] * 5 + [BUY] * 2 + [HOLD] * 5
        + [BUY] * 30 + [HOLD] * 5 + [BUY] * 3
    )
    remaining, n = empirical_remaining(labels)
    assert n == 3  # BUY runs of 10, 20, 30 are longer than 3; the run of 2 is not
    assert remaining == 17  # median of 7, 17, 27


def test_empirical_remaining_needs_samples():
    labels = pd.Series([HOLD] * 10 + [BUY] * 5 + [HOLD] * 3)
    assert empirical_remaining(labels) == (None, 0)


def test_days_to_threshold():
    assert days_to_threshold(40, -3, 25) == 5
    assert days_to_threshold(40, 3, 25) is None
    assert days_to_threshold(0, 0, 25) is None
