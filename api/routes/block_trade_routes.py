"""Block trade workflow API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
router = APIRouter(prefix="/block-trade", tags=["Block Trading"])

class BlockSubmitRequest(BaseModel):
    symbol: str; side: str = Field(..., pattern="^(buy|sell)$")
    quantity: float = Field(..., gt=0); limit_price: Optional[float] = Field(None, gt=0)
    firm_name: str; contact: str = ""; ttl_seconds: int = Field(3600, ge=300, le=86400)

class BlockRespondRequest(BaseModel):
    firm_name: str; quantity: float = Field(..., gt=0)
    counter_price: float = Field(..., gt=0); notes: str = ""

class BlockAcceptRequest(BaseModel):
    response_id: str; agreed_price: Optional[float] = Field(None, gt=0)
    execute_now: bool = True

def _state():
    from app_state import get_app_state; return get_app_state()

@router.post("/", summary="Submit a block trade")
async def submit_block(req: BlockSubmitRequest):
    bt = _state().block_trade.submit(req.symbol, req.side, req.quantity, req.limit_price,
                                      req.firm_name, req.contact, req.ttl_seconds)
    return bt.to_dict()

@router.post("/{block_id}/respond", summary="Respond to a block trade")
async def respond_to_block(block_id: str, req: BlockRespondRequest):
    r = _state().block_trade.respond(block_id, req.firm_name, req.quantity,
                                      req.counter_price, req.notes)
    if not r: raise HTTPException(404, "Block trade not found or not open")
    return r.to_dict()

@router.post("/{block_id}/accept", summary="Accept a response and optionally execute")
async def accept_response(block_id: str, req: BlockAcceptRequest):
    state = _state()
    result = state.block_trade.accept(block_id, req.response_id, req.agreed_price)
    if not result: raise HTTPException(404, "Block trade or response not found")
    if req.execute_now:
        bt_data = state.block_trade.get(block_id)
        try:
            from tools.smart_order_router import Order, OrderSide
            order = Order(symbol=bt_data["symbol"], side=OrderSide(bt_data["side"]),
                          quantity=bt_data["quantity"],
                          price=bt_data["agreed_price"])
            decision = state.sor.route(order)
            exec_res = state.execution.execute(decision, order.side)
            state.block_trade.record_execution(block_id, decision.order_id, exec_res.total_filled)
            result["execution"] = {"order_id": decision.order_id,
                                   "filled": exec_res.total_filled, "success": exec_res.success}
        except Exception as e:
            result["execution_error"] = str(e)
    return result

@router.delete("/{block_id}", summary="Cancel a block trade")
async def cancel_block(block_id: str, firm_name: str = Query(...)):
    r = _state().block_trade.cancel(block_id, firm_name)
    if not r: raise HTTPException(404, "Block trade not found or not cancellable")
    return r

@router.get("/", summary="List block trades")
async def list_blocks(symbol: Optional[str] = None, status: Optional[str] = None):
    return {"blocks": _state().block_trade.list(symbol, status)}

@router.get("/{block_id}", summary="Get block trade details")
async def get_block(block_id: str):
    r = _state().block_trade.get(block_id)
    if not r: raise HTTPException(404, "Block trade not found")
    return r
