"""Admin endpoints — kill switch, risk config, system control."""
from fastapi import APIRouter, HTTPException

from api.models import RiskConfigResponse, RiskStatsResponse, RiskConfigUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])


def _get_state():
    from app_state import get_app_state
    return get_app_state()


@router.post("/halt", summary="Halt all order routing (kill switch)")
async def halt():
    """Immediately stop accepting new orders. In-flight executions are not affected."""
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    state.halted = True
    return {"ok": True, "status": "halted"}


@router.post("/resume", summary="Resume order routing after halt")
async def resume():
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    state.halted = False
    return {"ok": True, "status": "running"}


@router.get("/status", summary="Get system run/halt status")
async def system_status():
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"halted": state.halted}


@router.get("/risk", response_model=RiskStatsResponse, summary="Get risk engine statistics")
async def get_risk_stats():
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return state.risk.get_stats()


@router.get("/risk/config", response_model=RiskConfigResponse, summary="Get current risk config")
async def get_risk_config():
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    cfg = state.risk.config
    return RiskConfigResponse(
        enabled=cfg.enabled,
        max_order_qty=cfg.max_order_qty,
        max_order_notional=cfg.max_order_notional,
        price_band_pct=cfg.price_band_pct,
        max_daily_notional=cfg.max_daily_notional,
        max_position_qty=cfg.max_position_qty,
    )


@router.put("/risk/config", response_model=RiskConfigResponse, summary="Update risk parameters at runtime")
async def update_risk_config(update: RiskConfigUpdate):
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    changes = {k: v for k, v in update.model_dump().items() if v is not None}
    state.risk.update_config(**changes)
    cfg = state.risk.config
    return RiskConfigResponse(
        enabled=cfg.enabled,
        max_order_qty=cfg.max_order_qty,
        max_order_notional=cfg.max_order_notional,
        price_band_pct=cfg.price_band_pct,
        max_daily_notional=cfg.max_daily_notional,
        max_position_qty=cfg.max_position_qty,
    )


@router.post("/risk/reset-daily", summary="Reset daily notional counter")
async def reset_daily():
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    state.risk.reset_daily()
    return {"ok": True, "message": "Daily notional counter reset"}
