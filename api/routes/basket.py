"""Basket/portfolio trading API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
router = APIRouter(prefix="/basket", tags=["Basket Trading"])

class BasketLegInput(BaseModel):
    symbol: str; side: str = Field(..., pattern="^(buy|sell)$")
    quantity: float = Field(..., gt=0); price: Optional[float] = Field(None, gt=0)

class BasketRequest(BaseModel):
    name: str = "My Basket"
    legs: List[BasketLegInput] = Field(..., min_length=2, max_length=50)
    base_currency: str = "USD"; firm_name: str = "SORFIX"

def _state():
    from app_state import get_app_state; return get_app_state()

@router.post("/", summary="Submit a basket order")
async def submit_basket(req: BasketRequest):
    b = _state().basket_engine.create(req.name,
        [{"symbol": l.symbol, "side": l.side, "quantity": l.quantity, "price": l.price}
         for l in req.legs],
        req.base_currency, req.firm_name)
    # Execute all legs immediately via SOR
    state = _state()
    from tools.smart_order_router import Order, OrderSide
    import time as _t
    b_data = b.to_dict()
    for leg in b.legs:
        try:
            order = Order(symbol=leg.symbol, side=OrderSide(leg.side),
                          quantity=leg.quantity, price=leg.price,
                          base_currency=req.base_currency)
            decision = state.sor.route(order)
            result   = state.execution.execute(decision, order.side)
            vwap = result.total_cost / result.total_filled if result.total_filled > 0 else None
            state.basket_engine.record_leg(b.id, leg.symbol, decision.order_id,
                                           result.total_filled, vwap, result.success)
        except Exception as e:
            state.basket_engine.record_leg(b.id, leg.symbol, "", 0.0, None, False, str(e))
    return state.basket_engine.get(b.id)

@router.get("/{basket_id}", summary="Get basket status")
async def get_basket(basket_id: str):
    r = _state().basket_engine.get(basket_id)
    if not r: raise HTTPException(404, "Basket not found")
    return r

@router.get("/", summary="List all baskets")
async def list_baskets():
    return {"baskets": _state().basket_engine.list()}

@router.delete("/{basket_id}", summary="Cancel a pending basket")
async def cancel_basket(basket_id: str):
    r = _state().basket_engine.cancel(basket_id)
    if not r: raise HTTPException(404, "Basket not found or not cancellable")
    return r
