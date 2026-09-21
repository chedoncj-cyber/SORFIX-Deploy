"""
Stripe card payment endpoint.
POST /api/payment/create-payment-intent — creates a Stripe PaymentIntent and returns the client_secret.

Requires STRIPE_SECRET_KEY in .env
"""
import os
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
import httpx

logger = logging.getLogger("stripe_payment")
router = APIRouter(prefix="/api/payment", tags=["Payment"])

STRIPE_API = "https://api.stripe.com/v1/payment_intents"

PRICE_TABLE = {
    ("pan",    "day"):   900,
    ("pan",    "week"):  1900,
    ("pan",    "month"): 4900,
    ("pan",    "api"):   2500,
    ("world",  "day"):   1200,
    ("world",  "week"):  2500,
    ("world",  "month"): 5900,
    ("world",  "api"):   3000,
    ("bundle", "day"):   1500,
    ("bundle", "week"):  3500,
    ("bundle", "month"): 9900,
    ("bundle", "api"):   4500,
}


class PaymentIntentRequest(BaseModel):
    product:     str   = Field(..., pattern="^(pan|world|bundle)$")
    tier:        str   = Field(..., pattern="^(day|week|month|api)$")
    name:        str
    description: str
    amount:      float
    currency:    str = "USD"
    email:       str


@router.post("/create-payment-intent")
async def create_payment_intent(req: PaymentIntentRequest):
    secret_key = os.getenv("STRIPE_SECRET_KEY", "")
    if not secret_key:
        raise HTTPException(
            status_code=503,
            detail="Card payments not configured. Set STRIPE_SECRET_KEY in .env"
        )

    expected_cents = PRICE_TABLE.get((req.product, req.tier))
    if expected_cents is None:
        raise HTTPException(status_code=400, detail="Invalid product/tier combination")

    # Anti-tampering: verify client amount matches server price table
    if abs(req.amount * 100 - expected_cents) > 1:
        raise HTTPException(status_code=400, detail="Price mismatch")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                STRIPE_API,
                auth=(secret_key, ""),
                data={
                    "amount":   str(expected_cents),
                    "currency": "usd",
                    "description": req.name,
                    "receipt_email": req.email,
                    "metadata[product]": req.product,
                    "metadata[tier]":    req.tier,
                    "metadata[name]":    req.name,
                    "automatic_payment_methods[enabled]": "true",
                }
            )

        if resp.status_code not in (200, 201):
            logger.error("Stripe error %s: %s", resp.status_code, resp.text)
            raise HTTPException(status_code=502, detail=f"Stripe API error: {resp.status_code}")

        data = resp.json()
        client_secret = data.get("client_secret")
        if not client_secret:
            raise HTTPException(status_code=502, detail="No client_secret in Stripe response")

        logger.info("PaymentIntent created: %s  product=%s tier=%s $%.2f",
                    data.get("id"), req.product, req.tier, expected_cents / 100)
        return JSONResponse({"client_secret": client_secret})

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Stripe request timed out")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected Stripe error: %s", exc)
        raise HTTPException(status_code=500, detail="Card payment service error")
