"""Position tracking endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List

from api.models import PositionResponse

router = APIRouter(prefix="/positions", tags=["Positions"])


def _get_state():
    from app_state import get_app_state
    return get_app_state()


@router.get("/", response_model=List[PositionResponse], summary="List all open positions")
async def list_positions():
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return state.positions.get_all()


@router.get("/stats", summary="Position tracker statistics")
async def position_stats():
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return state.positions.get_stats()


@router.get("/{symbol}", response_model=PositionResponse, summary="Get position for a specific symbol")
async def get_position(symbol: str):
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    pos = state.positions.get_position(symbol.upper())
    if pos is None:
        raise HTTPException(status_code=404, detail=f"No position for '{symbol.upper()}'")
    return pos.to_dict()
