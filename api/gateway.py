# Copyright (c) 2026 CheDon1CJ. All Rights Reserved.
# Proprietary and confidential. Unauthorised copying, distribution,
# or use of this file is strictly prohibited. See LICENSE for details.
"""
FastAPI gateway for Pan SORFIX.
Provides REST endpoints + WebSocket streaming for live order book data.
"""
import asyncio
import collections
import json
import logging
import os
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api.routes.orders      import router as orders_router
from api.routes.market_data import router as market_data_router
from api.routes.health      import router as health_router
from api.routes.admin       import router as admin_router
from api.routes.positions   import router as positions_router
from api.routes.algo        import router as algo_router
from api.routes.payment        import router as payment_router
from api.routes.stripe_payment import router as stripe_payment_router
from api.routes.config         import router as config_router

_log_level = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(
    level=_log_level,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("gateway")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app_state import init_app_state
    logger.info("Pan SORFIX starting...")
    try:
        init_app_state()  # simulate flag driven by sor_config.yaml
    except RuntimeError as exc:
        logger.critical("Startup failed — check configs/: %s", exc)
        raise
    logger.info("App state initialized. Market data pipeline running.")
    yield
    from app_state import get_app_state, reset_app_state
    try:
        state = get_app_state()
    except RuntimeError:
        pass  # startup failed — nothing to clean up
    else:
        state.pipeline.stop()
        try:
            state.db.close()
        except Exception as exc:
            logger.warning("DB close error: %s", exc)
        for fn in (state.gse.disconnect, state.jse.disconnect,
                   state.ngx.disconnect, state.nse.disconnect,
                   state.cse.disconnect, state.egx.disconnect,
                   state.brvm.disconnect, state.bse.disconnect,
                   state.nsx.disconnect, state.sem.disconnect,
                   state.mse.disconnect, state.bvmt.disconnect,
                   state.dse.disconnect, state.zse.disconnect,
                   state.luse.disconnect):
            try:
                fn()
            except Exception as exc:
                logger.warning("Adapter disconnect error: %s", exc)
    finally:
        reset_app_state()
    logger.info("Shutdown complete.")


# ------------------------------------------------------------------ #
# Auth + rate-limit helpers                                           #
# ------------------------------------------------------------------ #

def _load_auth_config():
    import yaml
    from pathlib import Path
    cfg_path = Path(__file__).parent.parent / "configs" / "sor_config.yaml"
    try:
        with open(cfg_path) as f:
            raw = yaml.safe_load(f)
        auth = raw.get("auth", {})
        rl   = raw.get("rate_limit", {})
        return (
            bool(auth.get("enabled", False)),
            set(auth.get("api_keys", [])),
            bool(rl.get("enabled", True)),
            int(rl.get("requests_per_minute", 300)),
        )
    except Exception:
        return False, set(), True, 300


_AUTH_ENABLED, _API_KEYS, _RL_ENABLED, _RL_RPM = _load_auth_config()
# Per-IP sliding window: deque of timestamps within the last 60s
_rate_buckets: dict = collections.defaultdict(collections.deque)
_rate_last_cleanup: float = 0.0  # epoch seconds of last purge


app = FastAPI(
    title="Pan SORFIX",
    description=(
        "Pan-African Low-Latency Smart Order Router — **Version 3.0**.\n\n"
        "Routes orders across GSE, JSE, NGX, NSE using 6-factor venue scoring: "
        "liquidity 28% · spread 18% · FX 18% · fee 16% · latency 10% · reliability 10%.\n\n"
        "**Active exchanges:** GSE (Ghana · GHS) · JSE (South Africa · ZAR) · NGX (Nigeria · NGN) · NSE (Kenya · KES).\n"
        "All four venues wired with FIX 4.2 adapters, GBM price simulation, and 10-level order books.\n\n"
        "**v3 upgrades:** 6-factor SOR · GBM market data · 99.8% fill rate · per-pair PAPSS FX costs · "
        "284 listed companies · proportional allocation · staleness multiplier · Live Roles portal tab."
    ),
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def auth_and_rate_limit(request: Request, call_next):
    # Skip auth/rate-limit for health, docs, portal, root
    skip_paths = {"/", "/health", "/ready", "/portal", "/docs",
                  "/openapi.json", "/redoc",
                  "/api/config",
                  "/api/payment/create-charge",
                  "/api/payment/create-payment-intent"}
    if request.url.path in skip_paths or request.url.path.startswith("/ws"):
        return await call_next(request)

    # API key auth
    if _AUTH_ENABLED:
        key = request.headers.get("X-API-Key", "")
        if key not in _API_KEYS:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing X-API-Key"})

    # Sliding-window rate limit per client IP
    if _RL_ENABLED:
        global _rate_last_cleanup
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        bucket = _rate_buckets[client_ip]
        # Remove timestamps older than 60s from this bucket
        while bucket and now - bucket[0] > 60.0:
            bucket.popleft()
        if len(bucket) >= _RL_RPM:
            return JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit exceeded — max {_RL_RPM} requests/minute"},
            )
        bucket.append(now)
        # Periodically purge stale IP entries to prevent unbounded dict growth
        if now - _rate_last_cleanup > 300.0:
            _rate_last_cleanup = now
            dead = [ip for ip, b in _rate_buckets.items() if not b]
            for ip in dead:
                del _rate_buckets[ip]

    return await call_next(request)


app.include_router(health_router)
app.include_router(orders_router)
app.include_router(market_data_router)
app.include_router(admin_router)
app.include_router(positions_router)
app.include_router(algo_router)
app.include_router(payment_router)
app.include_router(stripe_payment_router)
app.include_router(config_router)


@app.get("/portal", include_in_schema=False)
async def portal():
    from pathlib import Path
    resp = FileResponse(Path(__file__).parent.parent / "portal" / "index.html")
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    return resp

# Serve portal static assets (jobs_data.js, etc.)
from pathlib import Path as _Path
_portal_dir = _Path(__file__).parent.parent / "portal"
app.mount("/portal", StaticFiles(directory=str(_portal_dir)), name="portal-static")


@app.get("/tca", tags=["Analytics"], summary="Transaction Cost Analysis — recent orders")
async def tca(symbol: str = None, limit: int = Query(default=200, ge=1, le=1000)):
    """Return TCA data for recent orders. Filter by symbol with ?symbol=GCB."""
    from app_state import get_app_state
    try:
        state = get_app_state()
    except RuntimeError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=str(exc))
    raw = state.db.tca(symbol=symbol, limit=limit)
    rows = []
    for r in raw:
        fill_ratio = r.get("fill_ratio") or 0.0
        filled     = r.get("total_filled") or 0.0
        quantity   = round(filled / fill_ratio) if fill_ratio > 0 else filled
        success    = r.get("success", 0)
        if success:
            status = "FILLED"
        elif filled > 0:
            status = "PARTIAL"
        else:
            status = "REJECTED"
        rows.append({
            "order_id":   r.get("order_id"),
            "symbol":     r.get("symbol"),
            "side":       r.get("side"),
            "timestamp":  r.get("timestamp"),
            "filled_qty": filled,
            "quantity":   quantity,
            "fill_ratio": fill_ratio,
            "avg_price":  r.get("vwap"),
            "total_cost": r.get("total_cost"),
            "venue":      r.get("primary_venue"),
            "is_split":   r.get("is_split"),
            "latency_ms": (r.get("routing_latency_us") or 0.0) / 1000.0,
            "status":     status,
        })
    return {"rows": rows}


@app.websocket("/ws/book/{venue}/{symbol}")
async def stream_order_book(websocket: WebSocket, venue: str, symbol: str):
    """
    WebSocket stream: pushes order book snapshot every 500ms.
    Connect: ws://localhost:9090/ws/book/GSE/GCB
    Closes with code 1008 if venue is unknown or disabled.
    """
    from app_state import get_app_state
    venue  = venue.upper()
    symbol = symbol.upper()

    try:
        state = get_app_state()
    except RuntimeError:
        await websocket.accept()
        await websocket.close(code=1011, reason="Server not initialized")
        return

    vcfg = state.sor.venues.get(venue)
    if vcfg is None or not vcfg.enabled:
        await websocket.accept()
        await websocket.close(code=1008, reason=f"Venue '{venue}' not found or disabled")
        return

    if symbol not in state.pipeline.get_valid_symbols(venue):
        await websocket.accept()
        await websocket.close(code=1008, reason=f"Symbol '{symbol}' not found on venue '{venue}'")
        return

    await websocket.accept()
    logger.info("WS connected: %s:%s", venue, symbol)
    try:
        while True:
            book = state.cache.get(venue, symbol)
            if book:
                payload = {
                    "venue":    book.venue,
                    "symbol":   book.symbol,
                    "best_bid": book.best_bid.price if book.best_bid else None,
                    "best_ask": book.best_ask.price if book.best_ask else None,
                    "spread":   book.spread,
                    "bids":     [{"price": l.price, "qty": l.quantity} for l in book.bids[:5]],
                    "asks":     [{"price": l.price, "qty": l.quantity} for l in book.asks[:5]],
                }
                await websocket.send_text(json.dumps(payload))
            else:
                await websocket.send_text(json.dumps({"venue": venue, "symbol": symbol, "status": "no_data"}))
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        logger.info("WS disconnected: %s:%s", venue, symbol)
    except Exception:
        logger.exception("WS error %s:%s", venue, symbol)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass


@app.get("/", tags=["Root"])
async def root(request: Request):
    base_url = str(request.base_url).rstrip("/")
    ws_base  = base_url.replace("http://", "ws://").replace("https://", "wss://")
    return {
        "app":         "Pan SORFIX",
        "version":     "3.0.0",
        "description": "Pan SORFIX — Pan-African Smart Order Router",
        "docs":        "/docs",
        "portal":      "/portal",
        "health":      "/health",
        "ready":       "/ready",
        "websocket":   f"{ws_base}/ws/book/{{venue}}/{{symbol}}",
        "endpoints": {
            "orders":    "/orders/submit  /orders/route  /orders/{id}",
            "algo":      "/algo/twap  /algo/vwap  /algo/{id}/cancel",
            "positions": "/positions/",
            "admin":     "/admin/halt  /admin/resume  /admin/risk",
            "tca":       "/tca?symbol=GCB",
            "market":    "/market-data/book/{venue}/{symbol}",
        },
        "exchanges":   {
            "GSE": "active (Ghana Stock Exchange — GHS)",
            "JSE": "active (Johannesburg Stock Exchange — ZAR)",
            "NGX": "active (Nigerian Exchange Group — NGN)",
            "NSE": "active (Nairobi Securities Exchange — KES)",
        },
    }
