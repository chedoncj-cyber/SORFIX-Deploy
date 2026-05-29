"""Algorithmic order execution endpoints — TWAP and VWAP."""
from fastapi import APIRouter, HTTPException
from typing import List

from api.models import AlgoOrderRequest, AlgoOrderResponse

router = APIRouter(prefix="/algo", tags=["Algo Orders"])


def _get_state():
    from app_state import get_app_state
    return get_app_state()


def _to_response(order) -> dict:
    return order.to_dict()


@router.post("/twap", response_model=AlgoOrderResponse, summary="Submit a TWAP order")
async def submit_twap(req: AlgoOrderRequest):
    """Split a large order into equal-size time slices spread over duration_seconds."""
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    if state.halted:
        raise HTTPException(status_code=503, detail="System halted — order routing disabled")
    order = state.algo.submit_twap(
        symbol=req.symbol.upper(),
        side=req.side.value,
        total_qty=req.total_qty,
        duration_seconds=req.duration_seconds,
        slices=req.slices,
        price=req.price,
        base_currency=req.base_currency,
    )
    return _to_response(order)


@router.post("/vwap", response_model=AlgoOrderResponse, summary="Submit a VWAP order")
async def submit_vwap(req: AlgoOrderRequest):
    """Split a large order using a volume-weighted Gaussian profile over duration_seconds."""
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    if state.halted:
        raise HTTPException(status_code=503, detail="System halted — order routing disabled")
    order = state.algo.submit_vwap(
        symbol=req.symbol.upper(),
        side=req.side.value,
        total_qty=req.total_qty,
        duration_seconds=req.duration_seconds,
        slices=req.slices,
        price=req.price,
        base_currency=req.base_currency,
    )
    return _to_response(order)


@router.get("/", summary="List all algo orders")
async def list_algo_orders():
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    orders = state.algo.get_all()
    return {"count": len(orders), "orders": orders}


@router.get("/active", summary="List running algo orders")
async def list_active():
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"orders": state.algo.get_active()}


@router.get("/{algo_id}", response_model=AlgoOrderResponse, summary="Get algo order status")
async def get_algo_order(algo_id: str):
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    order = state.algo.get(algo_id.upper())
    if order is None:
        raise HTTPException(status_code=404, detail=f"Algo order '{algo_id}' not found")
    return _to_response(order)


@router.post("/{algo_id}/cancel", summary="Cancel a running algo order")
async def cancel_algo_order(algo_id: str):
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    cancelled = state.algo.cancel(algo_id.upper())
    if not cancelled:
        raise HTTPException(
            status_code=404,
            detail=f"Algo order '{algo_id}' not found or already terminal",
        )
    return {"ok": True, "algo_id": algo_id.upper(), "status": "cancelled"}
