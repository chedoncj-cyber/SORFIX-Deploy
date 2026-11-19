"""Admin endpoints — kill switch, risk config, system control."""
import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pathlib import Path

from api.models import RiskConfigResponse, RiskStatsResponse, RiskConfigUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])

# Vector 10 — Dedicated audit logger for admin mutations
_audit_log = logging.getLogger("sorfix.admin.audit")

# Vector 11 — ETag optimistic concurrency: version counter for risk config
_risk_config_version: int = 0


def _get_state():
    from app_state import get_app_state
    return get_app_state()


@router.post("/halt", summary="Halt all order routing (kill switch)")
async def halt(request: Request):
    """Immediately stop accepting new orders. In-flight executions are not affected."""
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    # Vector 10 — Audit log
    client_ip = request.client.host if request.client else "unknown"
    _audit_log.info("HALT called | ip=%s method=%s", client_ip, request.method)
    state.halted = True
    return {"ok": True, "status": "halted"}


@router.post("/resume", summary="Resume order routing after halt")
async def resume(request: Request):
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    # Vector 10 — Audit log
    client_ip = request.client.host if request.client else "unknown"
    _audit_log.info("RESUME called | ip=%s method=%s", client_ip, request.method)
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
async def update_risk_config(update: RiskConfigUpdate, request: Request):
    global _risk_config_version
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    # Vector 11 — ETag optimistic concurrency
    if_match = request.headers.get("if-match")
    current_etag = f'"{_risk_config_version}"'
    if if_match is not None and if_match != current_etag:
        return JSONResponse(
            status_code=412,
            content={"detail": "Precondition Failed — risk config version mismatch"},
            headers={"ETag": current_etag},
        )

    changes = {k: v for k, v in update.model_dump().items() if v is not None}
    # Vector 10 — Audit log
    client_ip = request.client.host if request.client else "unknown"
    _audit_log.info(
        "UPDATE_RISK_CONFIG called | ip=%s method=%s params=%s",
        client_ip, request.method, changes,
    )
    state.risk.update_config(**changes)
    _risk_config_version += 1
    cfg = state.risk.config
    new_etag = f'"{_risk_config_version}"'
    response_body = RiskConfigResponse(
        enabled=cfg.enabled,
        max_order_qty=cfg.max_order_qty,
        max_order_notional=cfg.max_order_notional,
        price_band_pct=cfg.price_band_pct,
        max_daily_notional=cfg.max_daily_notional,
        max_position_qty=cfg.max_position_qty,
    )
    return JSONResponse(
        content=response_body.model_dump(),
        headers={"ETag": new_etag},
    )


@router.post("/risk/reset-daily", summary="Reset daily notional counter")
async def reset_daily():
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    state.risk.reset_daily()
    return {"ok": True, "message": "Daily notional counter reset"}


@router.get("/reconcile", tags=["Admin"], summary="Run order reconciliation")
async def reconcile(request: Request):
    from app_state import get_app_state
    from tools.reconciliation import run as run_recon
    state = get_app_state()
    db_path = str(Path(__file__).parent.parent.parent / "data" / "sorfix.db")
    result = run_recon(state.order_store if hasattr(state, "order_store") else {}, db_path)
    return result


@router.get("/audit-log", tags=["Admin"], summary="Last 100 admin audit log entries")
async def audit_log(limit: int = 100):
    from tools.admin_audit_log import tail
    return {"entries": tail(limit)}


@router.post("/backup", tags=["Admin"], summary="Trigger immediate database backup")
async def backup_now():
    from tools.backup_db import run as run_backup
    return run_backup()
