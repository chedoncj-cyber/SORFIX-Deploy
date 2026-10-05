"""
Asset class definitions and per-asset configuration.
Provides the AssetClass enum and tick/lot/settlement rules used by handlers,
the risk engine, and the multi-asset order router.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict


class AssetClass(str, Enum):
    EQUITY  = "equity"
    BOND    = "bond"
    FX      = "fx"
    FUTURES = "futures"


@dataclass(frozen=True)
class AssetConfig:
    asset_class:      AssetClass
    min_lot:          float   # minimum order quantity
    tick_size:        float   # minimum price increment
    settlement_days:  int     # T+N settlement
    price_in_pct:     bool    # True for bonds (price quoted as % of face)
    quote_currency:   bool    # True for FX (notional in quote leg)
    fix_security_type: str    # FIX tag 167 value


ASSET_CONFIG: Dict[AssetClass, AssetConfig] = {
    AssetClass.EQUITY: AssetConfig(
        asset_class=AssetClass.EQUITY,
        min_lot=1,
        tick_size=0.01,
        settlement_days=2,
        price_in_pct=False,
        quote_currency=False,
        fix_security_type="CS",      # Common Stock
    ),
    AssetClass.BOND: AssetConfig(
        asset_class=AssetClass.BOND,
        min_lot=1_000,               # face value units
        tick_size=0.0001,            # 1/100th of a point (bond price in %)
        settlement_days=2,
        price_in_pct=True,
        quote_currency=False,
        fix_security_type="CORP",    # also GOVT, MBS, MUNI
    ),
    AssetClass.FX: AssetConfig(
        asset_class=AssetClass.FX,
        min_lot=1_000,               # micro lot = 1k base currency units
        tick_size=0.00001,           # 1 pip for 5-decimal pairs
        settlement_days=2,           # spot FX T+2
        price_in_pct=False,
        quote_currency=True,
        fix_security_type="FOR",     # Foreign Exchange Contract
    ),
    AssetClass.FUTURES: AssetConfig(
        asset_class=AssetClass.FUTURES,
        min_lot=1,
        tick_size=0.25,
        settlement_days=0,           # daily mark-to-market
        price_in_pct=False,
        quote_currency=False,
        fix_security_type="FUT",
    ),
}


def get_config(asset_class: AssetClass) -> AssetConfig:
    return ASSET_CONFIG[asset_class]


def round_to_tick(price: float, asset_class: AssetClass) -> float:
    tick = ASSET_CONFIG[asset_class].tick_size
    return round(round(price / tick) * tick, 10)


def round_to_lot(quantity: float, asset_class: AssetClass) -> float:
    lot = ASSET_CONFIG[asset_class].min_lot
    return max(lot, round(quantity / lot) * lot)
