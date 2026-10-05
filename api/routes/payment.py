"""
Coinbase Commerce payment endpoint.
POST /api/payment/create-charge — creates a hosted checkout charge and returns the URL.

Requires COINBASE_COMMERCE_API_KEY in .env
"""
import os
import logging
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger("payment")
router = APIRouter(prefix="/api/payment", tags=["Payment"])

COINBASE_API = "https://api.commerce.coinbase.com/charges"
COINBASE_VERSION = "2018-03-22"

PRICE_TABLE = {
    ("pan",    "day"):   9,
    ("pan",    "week"):  19,
    ("pan",    "month"): 49,
    ("pan",    "api"):   25,
    ("world",  "day"):   12,
    ("world",  "week"):  25,
    ("world",  "month"): 59,
    ("world",  "api"):   30,
    ("bundle", "day"):   15,
    ("bundle", "week"):  35,
    ("bundle", "month"): 99,
    ("bundle", "api"):   45,
}


class ChargeRequest(BaseModel):
    product: str = Field(..., pattern="^(pan|world|bundle)$")
    tier:    str = Field(..., pattern="^(day|week|month|api)$")
    name:    str
    description: str
    amount:  float
    currency: str = "USD"
    crypto:  str = "BTC"


@router.post("/create-charge")
async def create_charge(req: ChargeRequest):
    api_key = os.getenv("COINBASE_COMMERCE_API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Payment service not configured. Set COINBASE_COMMERCE_API_KEY in .env"
        )

    # Verify amount matches price table (anti-tampering)
    expected = PRICE_TABLE.get((req.product, req.tier))
    if expected is None:
        raise HTTPException(status_code=400, detail="Invalid product/tier combination")
    if abs(req.amount - expected) > 0.01:
        raise HTTPException(status_code=400, detail="Price mismatch — do not modify request amounts")

    payload = {
        "name": req.name,
        "description": req.description,
        "pricing_type": "fixed_price",
        "local_price": {
            "amount": str(expected),
            "currency": "USD"
        },
        "metadata": {
            "product": req.product,
            "tier":    req.tier,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                COINBASE_API,
                json=payload,
                headers={
                    "X-CC-Api-Key":  api_key,
                    "X-CC-Version":  COINBASE_VERSION,
                    "Content-Type":  "application/json",
                    "Accept":        "application/json",
                }
            )
        if resp.status_code not in (200, 201):
            logger.error("Coinbase error %s: %s", resp.status_code, resp.text)
            raise HTTPException(status_code=502, detail=f"Coinbase Commerce error: {resp.status_code}")

        data = resp.json()
        hosted_url = data.get("data", {}).get("hosted_url")
        charge_id  = data.get("data", {}).get("id")

        if not hosted_url:
            raise HTTPException(status_code=502, detail="No hosted_url in Coinbase response")

        logger.info("Charge created: %s  product=%s tier=%s $%s", charge_id, req.product, req.tier, expected)
        return JSONResponse({"hosted_url": hosted_url, "charge_id": charge_id})

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Coinbase Commerce request timed out")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected payment error: %s", exc)
        raise HTTPException(status_code=500, detail="Payment service error")
