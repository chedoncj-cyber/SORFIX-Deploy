"""IOI board API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
router = APIRouter(prefix="/ioi", tags=["IOI Board"])

class IOIRequest(BaseModel):
    symbol: str; side: str = Field(..., pattern="^(buy|sell)$")
    quantity: float = Field(..., gt=0); price: Optional[float] = Field(None, gt=0)
    firm_name: str; contact: str = ""; notes: str = ""
    ttl_seconds: int = Field(3600, ge=60, le=86400)

def _state():
    from app_state import get_app_state; return get_app_state()

@router.post("/", summary="Post an Indication of Interest")
async def post_ioi(req: IOIRequest):
    ioi = _state().ioi_store.post(req.symbol, req.side, req.quantity, req.price,
                                   req.firm_name, req.contact, req.notes, req.ttl_seconds)
    return ioi.to_dict()

@router.get("/", summary="Browse IOI board")
async def list_iois(symbol: Optional[str]=None, side: Optional[str]=None, include_expired: bool=False):
    s = _state()
    return {"iois": s.ioi_store.list(symbol, side, include_expired), "stats": s.ioi_store.stats()}

@router.get("/{ioi_id}", summary="Get a single IOI")
async def get_ioi(ioi_id: str):
    ioi = _state().ioi_store.get(ioi_id)
    if not ioi: raise HTTPException(404, "IOI not found")
    return ioi

@router.delete("/{ioi_id}", summary="Cancel an IOI")
async def cancel_ioi(ioi_id: str, firm_name: str = Query(...)):
    r = _state().ioi_store.cancel(ioi_id, firm_name)
    if not r: raise HTTPException(404, "IOI not found or not yours")
    return r

@router.post("/match", summary="Match two opposite-side IOIs")
async def match_iois(ioi_id_1: str = Query(...), ioi_id_2: str = Query(...)):
    r = _state().ioi_store.match(ioi_id_1, ioi_id_2)
    if not r: raise HTTPException(422, "Cannot match — not found or same side")
    return r
