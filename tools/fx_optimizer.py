"""
FX optimization layer — simulates PAPSS (Pan-African Payment and Settlement System).
In production: replace mock rates with live PAPSS API calls.
"""
import logging
import threading
from typing import Dict, Tuple

_logger = logging.getLogger("fx_optimizer")


class FXOptimizer:
    # Approximate GHS/ZAR/NGN/KES rates vs USD (April 2026)
    _BASE_RATES_USD: Dict[str, float] = {
        "USD": 1.0,
        "GHS": 15.2,
        "ZAR": 18.8,
        "NGN": 1580.0,
        "KES": 133.5,
    }

    # Per-pair round-trip conversion cost as fraction of notional.
    # ZAR is the most liquid African FX pair; NGN has capital controls → higher spread.
    _PAIR_COSTS: Dict[Tuple[str, str], float] = {
        ("USD", "ZAR"): 0.0008,   # 8bps  — most liquid
        ("USD", "GHS"): 0.0012,   # 12bps
        ("USD", "KES"): 0.0015,   # 15bps
        ("USD", "NGN"): 0.0020,   # 20bps — capital controls, higher spread
        ("ZAR", "USD"): 0.0008,
        ("GHS", "USD"): 0.0012,
        ("KES", "USD"): 0.0015,
        ("NGN", "USD"): 0.0020,
        # Cross pairs routed via USD — additive costs
        ("GHS", "ZAR"): 0.0020,
        ("ZAR", "GHS"): 0.0020,
        ("GHS", "NGN"): 0.0032,
        ("NGN", "GHS"): 0.0032,
        ("GHS", "KES"): 0.0027,
        ("KES", "GHS"): 0.0027,
        ("ZAR", "NGN"): 0.0028,
        ("NGN", "ZAR"): 0.0028,
        ("ZAR", "KES"): 0.0023,
        ("KES", "ZAR"): 0.0023,
        ("NGN", "KES"): 0.0035,
        ("KES", "NGN"): 0.0035,
    }

    # Normalization denominator for venue scoring — represents a "worst acceptable" FX cost.
    # Any pair at or above this cost scores 0 on the FX factor.
    WORST_CASE_COST: float = 0.003  # 30bps

    def __init__(self, base_currency: str = "USD"):
        self.base_currency = base_currency
        self._rates: Dict[str, float] = dict(self._BASE_RATES_USD)
        self._lock = threading.RLock()

    def get_rate(self, from_ccy: str, to_ccy: str) -> float:
        with self._lock:
            if from_ccy == to_ccy:
                return 1.0
            usd_from = self._rates.get(from_ccy)
            usd_to   = self._rates.get(to_ccy)
            if usd_from is None:
                _logger.warning("Unknown currency '%s' — defaulting to USD rate 1.0", from_ccy)
                usd_from = 1.0
            if usd_to is None:
                _logger.warning("Unknown currency '%s' — defaulting to USD rate 1.0", to_ccy)
                usd_to = 1.0
            return usd_to / usd_from

    def get_conversion_cost(self, from_ccy: str, to_ccy: str) -> float:
        """Cost as a fraction of notional (0.0 = same currency, pair-specific for cross-currency)."""
        if from_ccy == to_ccy:
            return 0.0
        cost = self._PAIR_COSTS.get((from_ccy, to_ccy))
        if cost is None:
            _logger.warning("No pair cost for %s/%s — using worst-case 30bps", from_ccy, to_ccy)
            cost = self.WORST_CASE_COST
        return cost

    def convert(self, amount: float, from_ccy: str, to_ccy: str) -> float:
        return amount * self.get_rate(from_ccy, to_ccy)

    def update_rate(self, currency: str, usd_rate: float):
        with self._lock:
            self._rates[currency] = usd_rate

    def get_all_rates(self) -> Dict[str, float]:
        with self._lock:
            return dict(self._rates)
