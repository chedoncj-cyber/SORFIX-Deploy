"""Best execution reporting API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
router = APIRouter(prefix="/best-execution", tags=["Best Execution"])

def _state():
    from app_state import get_app_state; return get_app_state()

@router.get("/", summary="List best execution reports")
async def list_reports(symbol: Optional[str] = None, limit: int = Query(50, ge=1, le=500)):
    s = _state()
    return {"reports": s.best_exec.list(symbol, limit), "summary": s.best_exec.summary()}

@router.get("/summary", summary="Aggregate best execution statistics")
async def get_summary():
    return _state().best_exec.summary()

@router.get("/{order_id}", summary="Get best execution report for one order")
async def get_report(order_id: str):
    r = _state().best_exec.get(order_id)
    if not r: raise HTTPException(404, f"No report found for order {order_id}")
    return r
