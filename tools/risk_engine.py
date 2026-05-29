"""
Pre-trade risk engine — fat-finger, notional, price-band, and daily limit checks.
All checks are synchronous and must pass before any order is routed.
"""
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("risk_engine")


@dataclass
class RiskConfig:
    enabled: bool = True
    max_order_qty: float = 1_000_000.0
    max_order_notional: float = 10_000_000.0   # USD
    price_band_pct: float = 0.05               # ±5% from last trade
    max_daily_notional: float = 50_000_000.0   # USD
    max_position_qty: float = 5_000_000.0      # per symbol


@dataclass
class RiskViolation:
    check: str
    detail: str


class RiskEngine:
    def __init__(self, config: RiskConfig = None):
        self.config = config or RiskConfig()
        self._lock = threading.Lock()
        self._daily_notional: float = 0.0
        self._daily_reset_ts: float = time.time()
        self._checks_total: int = 0
        self._blocks_total: int = 0

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def check(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: Optional[float],
        base_currency: str = "USD",
        last_trade_price: Optional[float] = None,
        current_position_qty: float = 0.0,
    ) -> Optional[RiskViolation]:
        """Return a RiskViolation if the order fails pre-trade risk, else None."""
        if not self.config.enabled:
            return None

        with self._lock:
            self._checks_total += 1
            self._maybe_reset_daily()

            violation = (
                self._check_qty(quantity)
                or self._check_notional(quantity, price)
                or self._check_price_band(price, last_trade_price)
                or self._check_daily_notional(quantity, price)
                or self._check_position(side, quantity, current_position_qty)
            )

            if violation:
                self._blocks_total += 1
                logger.warning(
                    "Risk block [%s] %s %s qty=%.0f price=%s: %s",
                    symbol, side.upper(), violation.check,
                    quantity, price, violation.detail,
                )
            return violation

    def record_fill(self, quantity: float, price: Optional[float]):
        """Call after a successful execution to update daily notional."""
        if price is None or quantity <= 0:
            return
        with self._lock:
            self._daily_notional += quantity * price

    def reset_daily(self):
        """Manually reset daily counters (e.g. at market open)."""
        with self._lock:
            self._daily_notional = 0.0
            self._daily_reset_ts = time.time()

    def get_stats(self) -> dict:
        with self._lock:
            return {
                "enabled": self.config.enabled,
                "checks_total": self._checks_total,
                "blocks_total": self._blocks_total,
                "daily_notional": round(self._daily_notional, 2),
                "daily_notional_limit": self.config.max_daily_notional,
                "daily_reset_ts": self._daily_reset_ts,
            }

    def update_config(self, **kwargs):
        """Hot-update risk parameters at runtime."""
        with self._lock:
            for k, v in kwargs.items():
                if hasattr(self.config, k):
                    setattr(self.config, k, v)
                    logger.info("Risk config updated: %s = %s", k, v)
                else:
                    logger.warning("Unknown risk config key: %s", k)

    # ------------------------------------------------------------------ #
    # Internal checks                                                      #
    # ------------------------------------------------------------------ #

    def _check_qty(self, quantity: float) -> Optional[RiskViolation]:
        if quantity > self.config.max_order_qty:
            return RiskViolation(
                "max_order_qty",
                f"qty {quantity:.0f} exceeds limit {self.config.max_order_qty:.0f}",
            )
        return None

    def _check_notional(self, quantity: float, price: Optional[float]) -> Optional[RiskViolation]:
        if price is None:
            return None
        notional = quantity * price
        if notional > self.config.max_order_notional:
            return RiskViolation(
                "max_order_notional",
                f"notional {notional:,.2f} exceeds limit {self.config.max_order_notional:,.2f}",
            )
        return None

    def _check_price_band(
        self, price: Optional[float], last_trade: Optional[float]
    ) -> Optional[RiskViolation]:
        if price is None or last_trade is None or last_trade <= 0:
            return None
        deviation = abs(price - last_trade) / last_trade
        if deviation > self.config.price_band_pct:
            return RiskViolation(
                "price_band",
                f"price {price} deviates {deviation*100:.1f}% from last {last_trade} "
                f"(limit ±{self.config.price_band_pct*100:.0f}%)",
            )
        return None

    def _check_daily_notional(self, quantity: float, price: Optional[float]) -> Optional[RiskViolation]:
        if price is None:
            return None
        projected = self._daily_notional + quantity * price
        if projected > self.config.max_daily_notional:
            return RiskViolation(
                "max_daily_notional",
                f"projected daily notional {projected:,.2f} would exceed limit "
                f"{self.config.max_daily_notional:,.2f}",
            )
        return None

    def _check_position(
        self, side: str, quantity: float, current_qty: float
    ) -> Optional[RiskViolation]:
        if side.lower() == "buy":
            projected = current_qty + quantity
        else:
            projected = current_qty - quantity
        if abs(projected) > self.config.max_position_qty:
            return RiskViolation(
                "max_position_qty",
                f"projected position {projected:,.0f} would exceed limit "
                f"±{self.config.max_position_qty:,.0f}",
            )
        return None

    def _maybe_reset_daily(self):
        """Auto-reset if calendar day has rolled over (UTC)."""
        now = time.time()
        if now - self._daily_reset_ts >= 86_400:
            self._daily_notional = 0.0
            self._daily_reset_ts = now
            logger.info("Risk engine: daily notional counter auto-reset")
