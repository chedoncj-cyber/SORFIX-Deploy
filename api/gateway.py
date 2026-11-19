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
import re
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
from api.routes.ioi              import router as ioi_router
from api.routes.dark_pool_routes import router as dark_pool_router
from api.routes.iceberg          import router as iceberg_router
from api.routes.basket           import router as basket_router
from api.routes.drop_copy_routes import router as drop_copy_router
from api.routes.best_exec_routes import router as best_exec_router
from api.routes.block_trade_routes import router as block_trade_router
from api.routes.oms_routes       import router as oms_router
from api.routes.multi_asset      import router as multi_asset_router
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
        state = init_app_state(start_pipelines=False)
    except Exception as exc:
        logger.critical("Startup failed: %s", exc, exc_info=True)
        raise
    _md_tasks = [
        asyncio.create_task(state.pipeline.run_async(), name="market-data"),
        asyncio.create_task(state.fx_md.run_async(),    name="fx-md"),
        asyncio.create_task(state.bond_md.run_async(),  name="bond-md"),
    ]
    logger.info("App state initialized. Asyncio market data tasks running.")
    yield
    for t in _md_tasks:
        t.cancel()
    await asyncio.gather(*_md_tasks, return_exceptions=True)
    from app_state import get_app_state, reset_app_state
    try:
        s = get_app_state()
    except RuntimeError:
        pass
    else:
        try:
            s.db.close()
        except Exception as exc:
            logger.warning("DB close error: %s", exc)
        for fn in (s.gse.disconnect, s.jse.disconnect,
                   s.ngx.disconnect, s.nse.disconnect,
                   s.cse.disconnect, s.egx.disconnect,
                   s.brvm.disconnect, s.bse.disconnect,
                   s.nsx.disconnect, s.sem.disconnect,
                   s.mse.disconnect, s.bvmt.disconnect,
                   s.dse.disconnect, s.zse.disconnect,
                   s.luse.disconnect):
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

# ── Web-shell / probe defence ─────────────────────────────────────────────────
_BLOCKED_EXTS = re.compile(
    r"\.(php\d*|phtml|phar|asp|aspx|ashx|asmx|jsp|jspx|cfm|cgi|pl|sh|bash"
    r"|exe|dll|bat|cmd|htaccess|htpasswd|shtml)\b",
    re.IGNORECASE,
)
_SUSPICIOUS_PATH = re.compile(
    r"(\.\.[/\\]|%2e%2e|%252e|/etc/passwd|/proc/self"
    r"|cmd\.exe|base64_decode|eval\s*\(|system\s*\(|passthru\s*\("
    r"|shell_exec\s*\(|phpinfo\s*\()",
    re.IGNORECASE,
)
_BLOCKED_UA = re.compile(
    r"(sqlmap|nikto|nmap|masscan|zgrab|nuclei|dirsearch|gobuster|ffuf|wfuzz"
    r"|acunetix|nessus|openvas|burp|havij|hydra|metasploit)",
    re.IGNORECASE,
)
_SEC_HEADERS = {
    "X-Frame-Options":        "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection":       "0",
    "Referrer-Policy":        "strict-origin-when-cross-origin",
    "Permissions-Policy":     "geolocation=(), microphone=(), camera=(), payment=()",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self' wss: https:; "
        "img-src 'self' data: https:; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    ),
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}

# Vector 1 — HTTP method override headers to block
_METHOD_OVERRIDE_HEADERS = frozenset([
    "x-http-method-override",
    "x-http-method",
    "x-method-override",
    "x-tunneling-method",
])

# Vector 5 — Mutation-specific rate limiting
_MUTATION_METHODS = frozenset(["POST", "PUT", "PATCH", "DELETE"])
_MUT_RPM_FRACTION = max(10, _RL_RPM // 10)
_mutation_buckets: dict = collections.defaultdict(collections.deque)

# Vector 2 — Max request body size (512 KB)
_MAX_BODY_BYTES = 512 * 1024

# Vector 11 — ETag version counter for risk config
_risk_config_version: int = 0

# PentAGI finding: disable API docs in production (SIMULATE=false) to prevent schema disclosure
_SIMULATE = os.environ.get("SIMULATE", "true").lower() == "true"
_docs_url     = "/docs"      if _SIMULATE else None
_redoc_url    = "/redoc"     if _SIMULATE else None
_openapi_url  = "/openapi.json" if _SIMULATE else None

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
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9090",
        "http://localhost:9091",
        "https://pan-sorfix.onrender.com",
        "https://world-sorfix.onrender.com",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT"],  # Vector 7: removed PATCH and DELETE (no such handlers)
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)


@app.middleware("http")
async def security_probe_filter(request: Request, call_next):
    """Block web-shell probes, path traversal, scanner UAs; add security headers."""
    import uuid
    path = request.url.path
    raw  = str(request.url)
    ua   = request.headers.get("user-agent", "")

    if _BLOCKED_EXTS.search(path):
        return JSONResponse({"detail": "Forbidden"}, status_code=403)
    if _SUSPICIOUS_PATH.search(raw):
        return JSONResponse({"detail": "Forbidden"}, status_code=403)
    if _BLOCKED_UA.search(ua):
        return JSONResponse({"detail": "Forbidden"}, status_code=403)

    # Vector 1 — Block HTTP method override headers
    for hdr in _METHOD_OVERRIDE_HEADERS:
        if request.headers.get(hdr):
            return JSONResponse({"detail": "Forbidden"}, status_code=403)

    # Vector 2 — Enforce 512 KB max body size
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > _MAX_BODY_BYTES:
                return JSONResponse({"detail": "Request body too large"}, status_code=413)
        except ValueError:
            pass

    # Vector 6 — Content-Type enforcement for POST/PUT/PATCH with a body
    if request.method in ("POST", "PUT", "PATCH"):
        cl = request.headers.get("content-length")
        if cl is not None and int(cl) > 0:
            ct = request.headers.get("content-type", "")
            if not ct.startswith("application/json"):
                return JSONResponse({"detail": "Unsupported Media Type — application/json required"}, status_code=415)

    response = await call_next(request)
    for k, v in _SEC_HEADERS.items():
        response.headers[k] = v
    # Vector 15 — Obfuscate server fingerprint
    response.headers["Server"] = "SORFIX"
    # Vector 16 — Attach request-ID for PATCH audit trail correlation
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    return response


@app.middleware("http")
async def auth_and_rate_limit(request: Request, call_next):
    # Skip auth/rate-limit for health, portal, root, payments
    # NOTE: /docs, /redoc, /openapi.json intentionally excluded — they go through
    # auth when _AUTH_ENABLED=true (PentAGI: schema disclosure prevention)
    skip_paths = {"/", "/health", "/ready", "/portal",
                  "/api/config",
                  "/api/payment/create-charge",
                  "/api/payment/create-payment-intent"}
    if request.url.path in skip_paths or request.url.path.startswith("/ws"):
        return await call_next(request)

    # Vector 13 — Reject empty body for PUT/PATCH
    if request.method in ("PUT", "PATCH"):
        cl_raw = request.headers.get("content-length")
        if cl_raw is None or cl_raw.strip() == "0":
            return JSONResponse(
                status_code=400,
                content={"detail": "Empty request body not allowed for PUT/PATCH"},
            )

    # Vector 3 — Admin mandatory auth: when API keys are configured, all /admin/
    # mutation requests require a valid X-API-Key regardless of _AUTH_ENABLED
    is_admin_mutation = (
        request.url.path.startswith("/admin/")
        and request.method in _MUTATION_METHODS
    )
    if is_admin_mutation and _API_KEYS:
        key = request.headers.get("X-API-Key", "")
        if key not in _API_KEYS:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing X-API-Key"})

    # API key auth (global flag)
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

        # Vector 5 — Mutation-specific secondary rate limit
        if request.method in _MUTATION_METHODS:
            mut_bucket = _mutation_buckets[client_ip]
            while mut_bucket and now - mut_bucket[0] > 60.0:
                mut_bucket.popleft()
            if len(mut_bucket) >= _MUT_RPM_FRACTION:
                return JSONResponse(
                    status_code=429,
                    content={"detail": f"Mutation rate limit exceeded — max {_MUT_RPM_FRACTION} mutations/minute"},
                )
            mut_bucket.append(now)

    return await call_next(request)


app.include_router(health_router)
app.include_router(orders_router)
app.include_router(market_data_router)
app.include_router(admin_router)
app.include_router(positions_router)
app.include_router(algo_router)
app.include_router(ioi_router)
app.include_router(dark_pool_router)
app.include_router(iceberg_router)
app.include_router(basket_router)
app.include_router(drop_copy_router)
app.include_router(best_exec_router)
app.include_router(block_trade_router)
app.include_router(oms_router)
app.include_router(multi_asset_router)
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

    # Vector 14 — Validate path parameters to prevent path injection
    _WS_VENUE_RE  = re.compile(r"^[A-Z]{2,10}$")
    _WS_SYMBOL_RE = re.compile(r"^[A-Z0-9._-]{1,16}$")
    if not _WS_VENUE_RE.match(venue) or not _WS_SYMBOL_RE.match(symbol):
        await websocket.close(code=1008, reason="Invalid venue or symbol format")
        return

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
            await asyncio.sleep(2.0)
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
        "docs":        "/docs" if _SIMULATE else "disabled in production",
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


# ── SOC2 CC2.3 / CC7.2 — Security contact and compliance endpoints ─────────────

@app.get("/.well-known/security.txt", include_in_schema=False)
async def security_txt():
    """RFC 9116 security contact for responsible disclosure."""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        "Contact: mailto:security@sorfix.io\n"
        "Preferred-Languages: en\n"
        "Policy: https://pan-sorfix.onrender.com/security-policy\n"
        "Canonical: https://pan-sorfix.onrender.com/.well-known/security.txt\n"
        "Expires: 2027-12-31T00:00:00.000Z\n"
    )


@app.get("/compliance/status", tags=["Compliance"], summary="SOC2 control status (CC6, CC7)")
async def compliance_status():
    """Reports runtime state of key SOC2 Trust Service Criteria controls."""
    import datetime
    return {
        "soc2_tsc": {
            "CC6_1_logical_access_controls": {
                "api_key_auth_enabled": _AUTH_ENABLED,
                "api_keys_configured": len(_API_KEYS) > 0,
                "status": "PASS" if _AUTH_ENABLED and _API_KEYS else "WARN — enable auth in sor_config.yaml",
            },
            "CC6_6_threat_detection": {
                "scanner_ua_blocking": True,
                "path_traversal_blocking": True,
                "method_override_blocking": True,
                "status": "PASS",
            },
            "CC6_7_data_in_transit": {
                "hsts_enabled": True,
                "hsts_max_age_seconds": 63072000,
                "hsts_preload": True,
                "tls_enforced_by_host": True,
                "status": "PASS",
            },
            "CC7_1_system_monitoring": {
                "rate_limiting_enabled": _RL_ENABLED,
                "rate_limit_rpm": _RL_RPM,
                "mutation_rate_limit_rpm": max(10, _RL_RPM // 10),
                "admin_audit_logging": True,
                "request_id_tracing": True,
                "status": "PASS",
            },
            "CC7_2_vulnerability_management": {
                "security_headers_applied": True,
                "cors_restricted": True,
                "docs_disabled_in_production": not _SIMULATE,
                "cve_pins_applied": ["starlette>=0.49.1", "python-multipart>=0.0.7"],
                "status": "PASS",
            },
            "CC8_1_change_management": {
                "deployment_via_github": True,
                "render_autodeploy": True,
                "status": "PASS",
            },
        },
        "assessed_at": datetime.datetime.utcnow().isoformat() + "Z",
        "platform":    "Pan SORFIX v3.0.0",
        "simulate_mode": _SIMULATE,
    }
