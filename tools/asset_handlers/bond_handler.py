"""
Fixed-income / bond order handler.
Translates clean price + face value into FIX 5.0 SP2 NewOrderSingle fields,
calculates accrued interest, and validates bond-specific constraints.

Supported bond types: CORP, GOVT, MUNI, MBS
FIX tags used:
  167 (SecurityType) = CORP | GOVT | MUNI | MBS
  107 (SecurityDesc) = ISIN or CUSIP
  228 (Factor)       = amortization factor for MBS
  236 (Yield)        = yield-to-maturity as decimal
  159 (AccruedInterestAmt) = accrued interest in currency units
  38  (OrderQty)     = face value in currency units (not share count)
  44  (Price)        = clean price as % of par (e.g. 98.50 = 98.5%)
"""
import math
import time
import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

logger = logging.getLogger("bond_handler")

# Supported bond security types (FIX tag 167 values)
BOND_TYPES = {"CORP", "GOVT", "MUNI", "MBS", "ABS", "CD"}

# Day-count conventions
DAY_COUNT_30_360 = "30/360"
DAY_COUNT_ACT_ACT = "ACT/ACT"
DAY_COUNT_ACT_360 = "ACT/360"


@dataclass
class BondOrderSpec:
    """All fields needed to place a bond order."""
    # Identity
    isin:            str             # ISIN or CUSIP
    bond_type:       str = "CORP"    # FIX SecurityType (167)
    description:     str = ""        # e.g. "Apple 3.85% 2046"

    # Pricing
    clean_price_pct: float = 100.0   # clean price as % of par
    face_value:      float = 10_000.0  # notional face value in currency units
    coupon_rate:     float = 0.0     # annual coupon rate, e.g. 0.0385 = 3.85%
    yield_to_mat:    Optional[float] = None  # YTM as decimal; if None, derived from price

    # Schedule
    issue_date:      Optional[date] = None
    maturity_date:   Optional[date] = None
    last_coupon_date: Optional[date] = None
    coupon_frequency: int = 2        # payments per year (2=semi-annual)

    # Settlement
    settlement_days: int = 2
    day_count_conv:  str = DAY_COUNT_30_360

    # Amortisation (MBS/ABS)
    factor:          float = 1.0     # remaining principal factor


@dataclass
class BondOrderResult:
    """Enriched bond order ready for FIX submission."""
    spec:            BondOrderSpec
    accrued_interest: float          # in currency units
    dirty_price_pct:  float          # clean + accrued (as % of par)
    total_consideration: float       # face_value * dirty_price_pct / 100
    settlement_date:  str            # YYYYMMDD
    fix_fields:       list = field(default_factory=list)  # (tag, value) pairs


class BondHandler:
    """
    Validates and enriches bond orders before FIX submission.
    Works alongside fix_engine.build_new_order_single() — call prepare() to get
    the FIX fields list, then pass it to build_raw_fix() directly.
    """

    def prepare(self, spec: BondOrderSpec) -> BondOrderResult:
        """Validate spec, calculate accrued interest, build FIX field list."""
        self._validate(spec)
        accrued  = self._accrued_interest(spec)
        dirty    = spec.clean_price_pct + (accrued / spec.face_value * 100)
        total    = spec.face_value * dirty / 100.0
        settle   = self._settlement_date(spec.settlement_days)

        fix_fields = [
            (167, spec.bond_type),           # SecurityType
            (107, spec.isin),                # SecurityDesc (ISIN/CUSIP)
            (64,  settle),                   # FutSettDate / SettlDate
            (159, f"{accrued:.4f}"),          # AccruedInterestAmt
        ]
        if spec.yield_to_mat is not None:
            fix_fields.append((236, f"{spec.yield_to_mat:.6f}"))  # Yield
        if spec.maturity_date:
            fix_fields.append((541, spec.maturity_date.strftime("%Y%m%d")))  # MaturityDate
        if spec.factor != 1.0:
            fix_fields.append((228, f"{spec.factor:.6f}"))  # Factor (MBS)

        logger.info(
            "Bond order prepared: %s %s face=%.0f clean=%.4f%% accrued=%.4f dirty=%.4f%%",
            spec.bond_type, spec.isin, spec.face_value,
            spec.clean_price_pct, accrued, dirty,
        )
        return BondOrderResult(
            spec=spec,
            accrued_interest=accrued,
            dirty_price_pct=dirty,
            total_consideration=total,
            settlement_date=settle,
            fix_fields=fix_fields,
        )

    # ── private helpers ────────────────────────────────────────────────

    def _validate(self, spec: BondOrderSpec):
        if spec.bond_type not in BOND_TYPES:
            raise ValueError(f"Unknown bond type '{spec.bond_type}'. Must be one of {BOND_TYPES}")
        if not spec.isin:
            raise ValueError("ISIN/CUSIP is required for bond orders")
        if spec.face_value < 1_000:
            raise ValueError(f"Minimum face value is 1,000; got {spec.face_value}")
        if not (0 <= spec.clean_price_pct <= 200):
            raise ValueError(f"Clean price {spec.clean_price_pct}% out of range (0–200)")
        if spec.coupon_frequency not in (1, 2, 4, 12):
            raise ValueError("coupon_frequency must be 1, 2, 4, or 12")

    def _accrued_interest(self, spec: BondOrderSpec) -> float:
        """Calculate accrued interest in currency units (face × coupon × time_fraction)."""
        if spec.coupon_rate == 0 or spec.last_coupon_date is None:
            return 0.0
        today = date.today()
        days_since = (today - spec.last_coupon_date).days
        period_days = 365.0 / spec.coupon_frequency
        coupon_per_period = spec.face_value * spec.coupon_rate / spec.coupon_frequency
        return coupon_per_period * (days_since / period_days)

    @staticmethod
    def _settlement_date(days: int) -> str:
        from datetime import timedelta
        d = date.today()
        added = 0
        while added < days:
            d += timedelta(days=1)
            if d.weekday() < 5:  # skip weekends
                added += 1
        return d.strftime("%Y%m%d")

    @staticmethod
    def price_to_yield(clean_price_pct: float, coupon_rate: float,
                       years_to_maturity: float, face: float = 100.0,
                       freq: int = 2) -> float:
        """Newton-Raphson YTM approximation for plain vanilla bonds."""
        if years_to_maturity <= 0:
            return 0.0
        n = int(years_to_maturity * freq)
        c = face * coupon_rate / freq
        p = clean_price_pct

        # Initial guess: current yield
        ytm = coupon_rate if clean_price_pct == 100 else c / p

        for _ in range(100):
            r = ytm / freq
            pv  = sum(c / (1 + r) ** (i + 1) for i in range(n))
            pv += face / (1 + r) ** n
            f   = pv - p
            # derivative
            dpv = sum(-(i + 1) * c / (1 + r) ** (i + 2) for i in range(n))
            dpv += -n * face / (1 + r) ** (n + 1)
            df  = dpv / freq
            step = f / df if df != 0 else 0
            ytm -= step
            if abs(step) < 1e-10:
                break
        return ytm
