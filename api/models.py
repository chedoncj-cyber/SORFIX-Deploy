"""
Pydantic request/response models for the Pan SORFIX REST API.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from enum import Enum



class OrderSideRequest(str, Enum):
    buy  = "buy"
    sell = "sell"


class AssetClassRequest(str, Enum):
    equity  = "equity"
    bond    = "bond"
    fx      = "fx"
    futures = "futures"


class OrderRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "symbol": "GCB",
            "side": "buy",
            "quantity": 1000,
            "price": 5.80,
            "base_currency": "USD",
            "asset_class": "equity",
            "max_splits": 3,
            "min_split_qty": 100.0,
        }
    })

    symbol:         str                      = Field(..., description="Ticker symbol, e.g. GCB")
    side:           OrderSideRequest
    quantity:       float                    = Field(..., gt=0)
    price:          Optional[float]          = Field(None, gt=0, description="Limit price; omit for market order")
    base_currency:  str                      = Field("USD")
    asset_class:    AssetClassRequest        = Field(AssetClassRequest.equity, description="Asset class")
    max_splits:     Optional[int]            = Field(None, ge=1, le=10, description="Max split legs; defaults to system config")
    min_split_qty:  Optional[float]          = Field(None, gt=0, description="Min qty per leg; defaults to system config")


# ------------------------------------------------------------------ #
# Bond order models                                                    #
# ------------------------------------------------------------------ #

class BondOrderRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "isin": "US912810TM85",
            "side": "buy",
            "face_value": 1_000_000,
            "clean_price_pct": 98.75,
            "bond_type": "GOVT",
            "coupon_rate": 4.5,
            "maturity_date": "20340815",
        }
    })
    isin:               str                 = Field(..., description="ISIN or CUSIP")
    side:               OrderSideRequest
    face_value:         float               = Field(..., gt=0, description="Principal amount in base currency")
    clean_price_pct:    float               = Field(..., gt=0, le=200, description="Clean price as % of face value")
    bond_type:          str                 = Field("CORP", description="CORP | GOVT | MUNI | MBS")
    coupon_rate:        float               = Field(0.0, ge=0, description="Annual coupon rate %")
    maturity_date:      Optional[str]       = Field(None, description="Maturity date YYYYMMDD")
    yield_to_maturity:  Optional[float]     = Field(None, description="YTM override (computed if omitted)")
    settlement_days:    int                 = Field(2, ge=0, le=5)
    day_count_conv:     str                 = Field("30/360")
    base_currency:      str                 = Field("USD")


class BondOrderResponse(BaseModel):
    order_id:           str
    isin:               str
    side:               str
    face_value:         float
    clean_price_pct:    float
    accrued_interest:   float
    dirty_price_pct:    float
    total_consideration: float
    settlement_date:    str
    yield_to_maturity:  Optional[float]
    success:            bool
    message:            str
    timestamp:          float


# ------------------------------------------------------------------ #
# FX order models                                                      #
# ------------------------------------------------------------------ #

class FXOrderRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "pair": "EURUSD",
            "side": "buy",
            "base_amount": 100_000,
            "spot_rate": 1.0875,
            "tenor": "SPOT",
        }
    })
    pair:               str                 = Field(..., description="Currency pair e.g. EURUSD or EUR/USD")
    side:               OrderSideRequest
    base_amount:        float               = Field(..., gt=0, description="Amount in base currency")
    spot_rate:          Optional[float]     = Field(None, gt=0, description="Spot rate (omit for market)")
    tenor:              str                 = Field("SPOT", description="SPOT | TOD | TOM | 1W | 1M | 3M | 1Y")
    forward_points:     Optional[float]     = Field(None, description="Forward points in pips (for forwards)")
    ndf:                bool                = Field(False, description="Non-Deliverable Forward")
    settlement_currency: Optional[str]     = Field(None, description="NDF settlement currency")
    base_currency:      str                 = Field("USD", description="Pricing currency for fees")


class FXOrderResponse(BaseModel):
    order_id:           str
    pair:               str
    side:               str
    base_ccy:           str
    quote_ccy:          str
    base_amount:        float
    notional_quote:     Optional[float]
    spot_rate:          Optional[float]
    settlement_date:    str
    lot_type:           str
    pip_size:           float
    is_em_pair:         bool
    success:            bool
    message:            str
    timestamp:          float


# ------------------------------------------------------------------ #
# OMS / EMS models                                                     #
# ------------------------------------------------------------------ #

class OMSRegisterRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "oms_id": "bloomberg-prod",
            "oms_type": "bloomberg_emsx",
            "display_name": "Bloomberg EMSX Production",
            "webhook_url": "https://emsx.example.com/callback",
        }
    })
    oms_id:         str             = Field(..., description="Unique OMS identifier")
    oms_type:       str             = Field(..., description="bloomberg_emsx | charles_river | fidessa | generic")
    display_name:   str             = Field(..., description="Human-readable OMS name")
    webhook_url:    Optional[str]   = Field(None, description="Async ExecutionReport push endpoint")
    api_key:        str             = Field("", description="OMS API key for webhook auth")


class OMSRegisterResponse(BaseModel):
    oms_id:         str
    oms_type:       str
    display_name:   str
    registered_at:  float
    message:        str


class OMSInboundRequest(BaseModel):
    oms_id:     str             = Field(..., description="Registered OMS identifier")
    payload:    dict            = Field(..., description="Raw OMS order payload (OMS-type-specific fields)")


class OMSConnectionResponse(BaseModel):
    oms_id:         str
    oms_type:       str
    display_name:   str
    webhook_url:    Optional[str]
    registered_at:  float
    orders_sent:    int
    last_activity:  float


class RoutingLegResponse(BaseModel):
    venue:          str
    symbol:         str
    quantity:       float
    price:          Optional[float]
    currency:       str
    estimated_cost: float


class VenueScoreResponse(BaseModel):
    venue:         str
    score:         float
    liquidity:     float
    spread:        float
    fee:           float
    fx_cost:       float
    latency:       float
    available_qty: float
    reliability:   float = 1.0


class RoutingDecisionResponse(BaseModel):
    order_id:            str
    symbol:              str
    total_quantity:      float
    primary_venue:       str
    legs:                List[RoutingLegResponse]
    routing_latency_us:  float
    is_split:            bool
    timestamp:           float
    venue_scores:        List[VenueScoreResponse]


class ExecutionReportResponse(BaseModel):
    leg_venue:   str
    status:      str
    filled_qty:  float
    avg_price:   Optional[float]  # None when the leg was not filled
    message:     str
    attempts:    int


class OrderResponse(BaseModel):
    order_id:     str
    side:         str
    routing:      RoutingDecisionResponse
    executions:   List[ExecutionReportResponse]
    total_filled: float
    total_cost:   float
    success:      bool
    fill_ratio:   float           # total_filled / total_quantity
    vwap:         Optional[float] # total_cost / total_filled; None if unfilled
    timestamp:    float


class OrderBookLevel(BaseModel):
    price:    float
    quantity: float
    venue:    str


class OrderBookResponse(BaseModel):
    symbol:   str
    venue:    str
    bids:     List[OrderBookLevel]
    asks:     List[OrderBookLevel]
    spread:   Optional[float]
    best_bid: Optional[float]
    best_ask: Optional[float]


class VenueStatusResponse(BaseModel):
    venue:                  str
    enabled:                bool
    currency:               str
    taker_fee_bps:          float
    latency_ms:             float
    circuit_breaker_state:  str


class HealthResponse(BaseModel):
    status:               str
    uptime_seconds:       float
    market_data_updates:  int
    executions:           int
    failures:             int
    cache_books:          int
    venues:               List[VenueStatusResponse]


class MetricsResponse(BaseModel):
    market_data:  dict
    execution:    dict
    cache:        dict
    fx_rates:     dict


# ------------------------------------------------------------------ #
# Risk                                                                #
# ------------------------------------------------------------------ #

class RiskConfigResponse(BaseModel):
    enabled: bool
    max_order_qty: float
    max_order_notional: float
    price_band_pct: float
    max_daily_notional: float
    max_position_qty: float


class RiskStatsResponse(BaseModel):
    enabled: bool
    checks_total: int
    blocks_total: int
    daily_notional: float
    daily_notional_limit: float
    daily_reset_ts: float


class RiskConfigUpdate(BaseModel):
    enabled: Optional[bool] = None
    max_order_qty: Optional[float] = Field(None, gt=0)
    max_order_notional: Optional[float] = Field(None, gt=0)
    price_band_pct: Optional[float] = Field(None, gt=0, le=1.0)
    max_daily_notional: Optional[float] = Field(None, gt=0)
    max_position_qty: Optional[float] = Field(None, gt=0)


# ------------------------------------------------------------------ #
# Positions                                                           #
# ------------------------------------------------------------------ #

class PositionResponse(BaseModel):
    symbol: str
    net_qty: float
    avg_cost: float
    realized_pnl: float
    total_buys: int
    total_sells: int
    total_volume: float


# ------------------------------------------------------------------ #
# Algo orders                                                         #
# ------------------------------------------------------------------ #

class AlgoOrderRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "symbol": "GCB",
            "side": "buy",
            "total_qty": 5000,
            "duration_seconds": 300,
            "slices": 10,
            "price": 5.80,
            "base_currency": "USD",
        }
    })
    symbol: str = Field(..., description="Ticker symbol")
    side: OrderSideRequest
    total_qty: float = Field(..., gt=0)
    duration_seconds: float = Field(..., gt=0, description="Total execution window in seconds")
    slices: int = Field(..., ge=2, le=100, description="Number of child orders")
    price: Optional[float] = Field(None, gt=0, description="Limit price; omit for market")
    base_currency: str = Field("USD")


class AlgoOrderResponse(BaseModel):
    algo_id: str
    algo_type: str
    symbol: str
    side: str
    total_qty: float
    price: Optional[float]
    base_currency: str
    duration_seconds: float
    slices: int
    status: str
    submitted_qty: float
    filled_qty: float
    total_cost: float
    vwap: Optional[float]
    fill_ratio: float
    start_ts: Optional[float]
    end_ts: Optional[float]
    child_orders: List[str]
    error: Optional[str]
