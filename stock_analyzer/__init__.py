"""Stock analyzer: classifies stocks as Buy, Hold or Sell."""
from .data import SyntheticProvider, YahooProvider, guess_currency
from .market import ScanResult, scan
from .recommendation import InsufficientDataError, Recommendation, analyze
from .scoring import BUY, HOLD, SELL, compute_scores

__all__ = [
    "BUY",
    "HOLD",
    "SELL",
    "InsufficientDataError",
    "Recommendation",
    "ScanResult",
    "SyntheticProvider",
    "YahooProvider",
    "analyze",
    "compute_scores",
    "guess_currency",
    "scan",
]
