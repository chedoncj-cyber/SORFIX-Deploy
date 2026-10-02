"""Iceberg order API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
router = APIRouter(prefix="/iceberg", tags=["Iceberg Orders"])

class IcebergRequest(BaseModel):
    symbol: str; side: str = Field(..., pattern="^(buy|sell)$")
    total_qty: float = Field(..., gt=0); display_qty: float = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)
    base_currency: str = "USD"; firm_name: str = "SORFIX"

class IcebergFillRequest(BaseModel):
    filled_qty: float = Field(..., gt=0); avg_price: float = Field(..., gt=0)

def _state():
    from app_state import get_app_state; return get_app_state()

@router.post("/", summary="Create an iceberg order")
async def create_iceberg(req: IcebergRequest):
    if req.display_qty >= req.total_qty:
        from fastapi import HTTPException as H
        raise H(422, "display_qty must be less than total_qty")
    o = _state().iceberg_manager.create(req.symbol, req.side, req.total_qty,
                                         req.display_qty, req.price,
                                         req.base_currency, req.firm_name)
    return o.to_dict()

@router.post("/{order_id}/fill", summary="Record fill for an iceberg slice")
async def record_fill(order_id: str, req: IcebergFillRequest):
    o = _state().iceberg_manager.record_fill(order_id, req.filled_qty, req.avg_price)
    if not o: raise HTTPException(404, "Iceberg order not found or not active")
    return o.to_dict()

@router.delete("/{order_id}", summary="Cancel an iceberg order")
async def cancel_iceberg(order_id: str):
    r = _state().iceberg_manager.cancel(order_id)
    if not r: raise HTTPException(404, "Iceberg order not found")
    return r

@router.get("/{order_id}", summary="Get iceberg order status")
async def get_iceberg(order_id: str):
    r = _state().iceberg_manager.get(order_id)
    if not r: raise HTTPException(404, "Iceberg order not found")
    return r

@router.get("/", summary="List iceberg orders")
async def list_icebergs(status: Optional[str] = None):
    return {"orders": _state().iceberg_manager.list(status)}
