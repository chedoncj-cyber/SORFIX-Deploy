"""
FX (Foreign Exchange) order handler.
Handles currency pair parsing, pip/lot calculations, and builds FIX 5.0 SP2
QuoteRequest + NewOrderSingle fields for spot FX execution.

Supported execution modes:
  - Spot      — T+2 settlement (default)
  - Forward   — T+N settlement with forward points
  - NDF       — Non-Deliverable Forward (EM currencies)

FIX tags used:
  167 (SecurityType) = FOR
  55  (Symbol)       = "EUR/USD" (ISO pair notation)
  15  (Currency)     = base currency (tag 15 = EUR for EUR/USD)
  120 (SettlCurrency)= quote currency (USD for EUR/USD)
  64  (SettlDate)    = settlement date YYYYMMDD
  38  (OrderQty)     = base currency amount
  44  (Price)        = spot rate (base quoted in quote currency)
  193 (SettlDate2)   = far-leg date for swaps
  193 (ForwardPts)   = forward points (tag 37 for FX Forward)
"""
import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, Dict, Tuple

logger = logging.getLogger("fx_handler")

# Standard pip sizes by pair type
PIP_SIZE: Dict[str, float] = {
    "JPY": 0.01,     # JPY pairs: 2 decimal places
    "DEFAULT": 0.0001,  # all others: 4 decimal places (5th = pipette)
}

# ECN venue preferences by pair liquidity tier
TIER1_PAIRS = {
    "EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCHF",
    "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY",
}
EM_PAIRS = {
    "USDGHS", "USDNGN", "USDZAR", "USDKES",   # African EM — SORFIX advantage
    "USDBRL", "USDMXN", "USDINR", "USDTRY",
}

# Standard lot sizes
LOT_STANDARD = 100_000   # 100k base currency units
LOT_MINI     = 10_000
LOT_MICRO    = 1_000

# Settlement offset days (calendar days, adjusted for weekends)
SPOT_SETTLE_DAYS = 2


@dataclass
class FXOrderSpec:
    """All fields needed to place an FX spot order."""
    pair:           str             # e.g. "EURUSD" or "EUR/USD"
    side:           str             # "buy" | "sell"  (buy = buy base, sell = sell base)
    base_amount:    float           # amount in base currency
    spot_rate:      Optional[float] = None   # None = market order (take best quote)
    tenor:          str  = "SPOT"   # SPOT | TOD | TOM | ON | 1W | 1M | 3M
    forward_points: Optional[float] = None  # pips to add for forwards
    ndf:            bool = False     # Non-Deliverable Forward
    settlement_currency: Optional[str] = None  # NDF cash settlement currency


@dataclass
class FXOrderResult:
    """Enriched FX order ready for FIX submission."""
    spec:           FXOrderSpec
    base_ccy:       str
    quote_ccy:      str
    pip_size:       float
    lot_type:       str             # STANDARD | MINI | MICRO
    notional_base:  float
    notional_quote: Optional[float]  # base_amount * spot_rate
    settlement_date: str            # YYYYMMDD
    is_em_pair:     bool
    fix_fields:     list


class FXHandler:
    """
    Validates and enriches FX spot/forward orders before FIX submission.
    Integrates with the SORFIX market data pipeline which provides live
    FX rates via fx_optimizer.py.
    """

    def prepare(self, spec: FXOrderSpec, live_rate: Optional[float] = None) -> FXOrderResult:
        """Validate, enrich, and build FIX field list for an FX order."""
        base, quote = self._parse_pair(spec.pair)
        pip = self._pip_size(quote)
        lot_type = self._classify_lot(spec.base_amount)
        settle = self._settlement_date(spec.tenor)
        rate = spec.spot_rate or live_rate

        notional_quote = round(spec.base_amount * rate, 2) if rate else None
        is_em = f"{base}{quote}" in EM_PAIRS

        fix_fields: list = [
            (167, "FOR"),                     # SecurityType
            (55,  f"{base}/{quote}"),          # Symbol
            (15,  base),                       # Currency (base)
            (120, quote),                      # SettlCurrency (quote)
            (64,  settle),                     # SettlDate
        ]
        if rate is not None:
            fix_fields.append((44, f"{rate:.5f}"))
        if spec.forward_points is not None:
            fix_fields.append((37, f"{spec.forward_points:.5f}"))   # ForwardPoints
        if spec.ndf:
            fix_fields.append((167, "FXNDF"))  # override SecurityType for NDF
            if spec.settlement_currency:
                fix_fields.append((120, spec.settlement_currency))

        logger.info(
            "FX order prepared: %s%s %s %.0f base (%s) @ %s settle=%s em=%s",
            base, quote, spec.side, spec.base_amount, lot_type,
            f"{rate:.5f}" if rate else "MKT", settle, is_em,
        )
        return FXOrderResult(
            spec=spec,
            base_ccy=base,
            quote_ccy=quote,
            pip_size=pip,
            lot_type=lot_type,
            notional_base=spec.base_amount,
            notional_quote=notional_quote,
            settlement_date=settle,
            is_em_pair=is_em,
            fix_fields=fix_fields,
        )

    def pnl_in_quote(self, base_amount: float, entry_rate: float,
                     exit_rate: float) -> float:
        """P&L in quote currency: positive = profit for a long."""
        return base_amount * (exit_rate - entry_rate)

    def pip_value(self, base_amount: float, pair: str,
                  rate: Optional[float] = None) -> float:
        """Value of 1 pip move in quote currency."""
        _, quote = self._parse_pair(pair)
        pip = self._pip_size(quote)
        if quote == "USD" or rate is None:
            return base_amount * pip
        return base_amount * pip / rate

    # ── private helpers ───────────────────────────────────────────────

    @staticmethod
    def _parse_pair(pair: str) -> Tuple[str, str]:
        pair = pair.replace("/", "").replace("-", "").upper()
        if len(pair) != 6:
            raise ValueError(f"FX pair must be 6 characters (e.g. EURUSD), got '{pair}'")
        return pair[:3], pair[3:]

    @staticmethod
    def _pip_size(quote_ccy: str) -> float:
        return PIP_SIZE.get(quote_ccy, PIP_SIZE["DEFAULT"])

    @staticmethod
    def _classify_lot(base_amount: float) -> str:
        if base_amount >= LOT_STANDARD:
            return "STANDARD"
        if base_amount >= LOT_MINI:
            return "MINI"
        return "MICRO"

    @staticmethod
    def _settlement_date(tenor: str) -> str:
        today = date.today()
        tenor_map: Dict[str, int] = {
            "TOD": 0, "ON": 0,
            "TOM": 1,
            "SPOT": 2,
            "1W":  7, "1M": 30, "2M": 60, "3M": 91,
            "6M": 182, "1Y": 365,
        }
        days = tenor_map.get(tenor.upper(), 2)
        d = today
        added = 0
        while added < days:
            d += timedelta(days=1)
            if d.weekday() < 5:
                added += 1
        return d.strftime("%Y%m%d")
