"""OMS/EMS integration endpoints."""
import time
from fastapi import APIRouter, HTTPException

from api.models import (
    OMSRegisterRequest, OMSRegisterResponse,
    OMSInboundRequest, OMSConnectionResponse,
)

router = APIRouter(prefix="/oms", tags=["OMS/EMS Integration"])


def _get_state():
    from app_state import get_app_state
    return get_app_state()


@router.post("/register", response_model=OMSRegisterResponse,
             summary="Register an OMS/EMS connection")
async def register_oms(req: OMSRegisterRequest):
    """
    Register an OMS/EMS system so it can submit orders via POST /oms/inbound.
    Supported OMS types: bloomberg_emsx | charles_river | fidessa | flextrade | generic.
    """
    from tools.oms_bridge import OMSConnection
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    conn = OMSConnection(
        oms_id=req.oms_id,
        oms_type=req.oms_type,
        display_name=req.display_name,
        webhook_url=req.webhook_url,
        api_key=req.api_key,
    )
    state.oms_bridge.registry.register(conn)
    return OMSRegisterResponse(
        oms_id=conn.oms_id,
        oms_type=conn.oms_type,
        display_name=conn.display_name,
        registered_at=conn.registered_at,
        message=f"OMS '{conn.oms_id}' registered successfully",
    )


@router.post("/inbound", summary="Submit an order from a registered OMS")
async def oms_inbound(req: OMSInboundRequest):
    """
    Accept an order from a registered OMS/EMS system.
    The payload format depends on the OMS type (Bloomberg EMSX fields,
    standard fields, or generic JSON).
    Returns the execution result and SORFIX order ID.
    """
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    result = await state.oms_bridge.inbound_order(
        oms_id=req.oms_id,
        payload=req.payload,
    )
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    return result


@router.get("/connections", response_model=list[OMSConnectionResponse],
            summary="List all registered OMS connections")
async def list_connections():
    """Return all registered OMS/EMS systems and their activity stats."""
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return [
        OMSConnectionResponse(
            oms_id=c.oms_id,
            oms_type=c.oms_type,
            display_name=c.display_name,
            webhook_url=c.webhook_url,
            registered_at=c.registered_at,
            orders_sent=c.orders_sent,
            last_activity=c.last_activity,
        )
        for c in state.oms_bridge.registry.all()
    ]
