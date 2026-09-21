"""
Pydantic request/response models for the Pan SORFIX REST API.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from enum import Enum



class OrderSideRequest(str, Enum):
    buy  = "buy"
    sell = "sell"


class OrderRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "symbol": "GCB",
            "side": "buy",
            "quantity": 1000,
            "price": 5.80,
            "base_currency": "USD",
            "max_splits": 3,
            "min_split_qty": 100.0,
        }
    })

    symbol:         str             = Field(..., description="Ticker symbol, e.g. GCB")
    side:           OrderSideRequest
    quantity:       float           = Field(..., gt=0)
    price:          Optional[float] = Field(None, gt=0, description="Limit price; omit for market order")
    base_currency:  str             = Field("USD")
    max_splits:     Optional[int]   = Field(None, ge=1, le=10, description="Max split legs; defaults to system config")
    min_split_qty:  Optional[float] = Field(None, gt=0, description="Min qty per leg; defaults to system config")


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
