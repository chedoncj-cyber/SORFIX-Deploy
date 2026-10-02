"""Dark pool API endpoints."""
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional
router = APIRouter(prefix="/dark-pool", tags=["Dark Pool"])

class DarkOrderRequest(BaseModel):
    symbol: str; side: str = Field(..., pattern="^(buy|sell)$")
    quantity: float = Field(..., gt=0); price: Optional[float] = Field(None, gt=0)
    firm_name: str = "SORFIX"; ttl_seconds: int = Field(300, ge=30, le=3600)

class CrossRequest(BaseModel):
    symbol: str; side: str = Field(..., pattern="^(buy|sell)$")
    quantity: float = Field(..., gt=0); midpoint: Optional[float] = Field(None, gt=0)

def _state():
    from app_state import get_app_state; return get_app_state()

@router.post("/add", summary="Add order to dark pool")
async def add_to_pool(req: DarkOrderRequest):
    o = _state().dark_pool.add(req.symbol, req.side, req.quantity, req.price,
                                req.firm_name, req.ttl_seconds)
    return o.to_dict()

@router.post("/cross", summary="Attempt to cross against dark pool")
async def try_cross(req: CrossRequest):
    r = _state().dark_pool.try_cross(req.symbol, req.side, req.quantity, req.midpoint)
    return {"crossed": r.crossed, "cross_qty": r.cross_qty, "cross_price": r.cross_price,
            "lit_qty": r.lit_qty, "counterparty": r.counterparty, "cross_id": r.cross_id}

@router.get("/pool", summary="View dark pool snapshot")
async def pool_snapshot(symbol: Optional[str] = None):
    return {"orders": _state().dark_pool.snapshot(symbol), "stats": _state().dark_pool.stats()}

@router.get("/crosses", summary="View crossing history")
async def crossing_log(limit: int = Query(50, ge=1, le=500)):
    return {"crosses": _state().dark_pool.crossing_log(limit), "stats": _state().dark_pool.stats()}
