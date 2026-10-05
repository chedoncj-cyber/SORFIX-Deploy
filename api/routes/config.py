"""
Public config endpoint — returns non-secret client-side keys.
GET /api/config  →  { stripe_publishable_key }

The Stripe publishable key (pk_...) is safe to expose publicly.
The secret key (sk_...) never leaves the server.
"""
import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["Config"])


@router.get("/config")
async def public_config():
    return JSONResponse({
        "stripe_publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY", ""),
        "payments_enabled": bool(
            os.getenv("STRIPE_SECRET_KEY") or os.getenv("COINBASE_COMMERCE_API_KEY")
        ),
        "stripe_enabled":   bool(os.getenv("STRIPE_SECRET_KEY")),
        "coinbase_enabled": bool(os.getenv("COINBASE_COMMERCE_API_KEY")),
    })
