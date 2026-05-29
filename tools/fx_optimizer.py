"""
FX optimization layer — simulates PAPSS (Pan-African Payment and Settlement System).
In production: replace mock rates with live PAPSS API calls.
"""
import logging
import threading
from typing import Dict

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
        """Cost as a fraction of notional (0.0 = same currency, ~0.0015 = cross-currency)."""
        if from_ccy == to_ccy:
            return 0.0
        return 0.001 + 0.0005  # 10bps base spread + 5bps per hop

    def convert(self, amount: float, from_ccy: str, to_ccy: str) -> float:
        return amount * self.get_rate(from_ccy, to_ccy)

    def update_rate(self, currency: str, usd_rate: float):
        with self._lock:
            self._rates[currency] = usd_rate

    def get_all_rates(self) -> Dict[str, float]:
        with self._lock:
            return dict(self._rates)
