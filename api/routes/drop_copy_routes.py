"""Drop copy (FIX compliance stream) API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
router = APIRouter(prefix="/drop-copy", tags=["Drop Copy"])

class EndpointRequest(BaseModel):
    url: str; label: str = ""; enabled: bool = True

def _state():
    from app_state import get_app_state; return get_app_state()

@router.post("/endpoints", summary="Register a drop copy endpoint")
async def register_endpoint(req: EndpointRequest):
    return _state().drop_copy.register(req.url, req.label, req.enabled)

@router.get("/endpoints", summary="List registered endpoints")
async def list_endpoints():
    return {"endpoints": _state().drop_copy.list_endpoints(), "stats": _state().drop_copy.stats()}

@router.delete("/endpoints", summary="Remove an endpoint")
async def remove_endpoint(url: str = Query(...)):
    removed = _state().drop_copy.remove(url)
    if not removed: raise HTTPException(404, "Endpoint not found")
    return {"removed": True, "url": url}

@router.get("/log", summary="View drop copy audit log")
async def get_log(limit: int = Query(100, ge=1, le=500)):
    return {"log": _state().drop_copy.get_log(limit), "stats": _state().drop_copy.stats()}
