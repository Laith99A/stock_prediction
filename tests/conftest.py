import numpy as np
import pandas as pd
import pytest


def make_ohlcv(log_returns: np.ndarray, start_price: float = 100.0, end: str = "2026-09-23") -> pd.DataFrame:
    close = start_price * np.exp(np.cumsum(log_returns))
    index = pd.bdate_range(end=end, periods=len(close))
    return pd.DataFrame(
        {
            "Open": close,
            "High": close * 1.01,
            "Low": close * 0.99,
            "Close": close,
            "Volume": np.full(len(close), 1_000_000.0),
        },
        index=index,
    )


@pytest.fixture
def uptrend() -> pd.DataFrame:
    rng = np.random.default_rng(1)
    return make_ohlcv(rng.normal(0.002, 0.005, 700))


@pytest.fixture
def downtrend() -> pd.DataFrame:
    rng = np.random.default_rng(2)
    return make_ohlcv(rng.normal(-0.002, 0.005, 700))


@pytest.fixture
def sideways() -> pd.DataFrame:
    rng = np.random.default_rng(3)
    close = 100 * np.exp(rng.normal(0, 0.01, 700))  # noise around a constant level
    returns = np.diff(np.log(close), prepend=np.log(100))
    return make_ohlcv(returns)
