#!/usr/bin/env python3
"""
Pan SORFIX
Pan-African Low-Latency Smart Order Router

Usage:
  python main.py                    # Start API server on port 9090
  python main.py --demo             # Print a demo routing decision and exit
  python main.py --port 8080        # Custom port
"""
import argparse
import sys
import os
import time

# Ensure the app root is on PYTHONPATH when run directly
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()


def _load_api_config() -> dict:
    """Read host/port/workers from sor_config.yaml; APP_HOST/APP_PORT env vars override YAML."""
    try:
        import yaml
        from pathlib import Path
        raw = yaml.safe_load((Path(__file__).parent / "configs" / "sor_config.yaml").read_text(encoding="utf-8"))
        api = raw.get("api", {})
        cfg = {
            "host":    str(api.get("host", "0.0.0.0")),
            "port":    int(api.get("port", 9090)),
            "workers": int(api.get("workers", 1)),
        }
    except Exception:
        cfg = {"host": "0.0.0.0", "port": 9090, "workers": 1}
    if os.environ.get("APP_HOST"):
        cfg["host"] = os.environ["APP_HOST"]
    if os.environ.get("APP_PORT"):
        cfg["port"] = int(os.environ["APP_PORT"])
    if os.environ.get("PORT"):  # Render.com sets PORT automatically — highest priority
        cfg["port"] = int(os.environ["PORT"])
    return cfg


def _setup_logging():
    import logging
    from logging.handlers import RotatingFileHandler
    from pathlib import Path

    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    level = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    fmt   = "%(asctime)s %(name)s %(levelname)s %(message)s"

    handlers = []
    if sys.stdout is not None:
        handlers.append(logging.StreamHandler(sys.stdout))

    # Rotating file log — 5 MB per file, keep 3 backups (15 MB total)
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    handlers.append(
        RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
    )

    logging.basicConfig(level=level, format=fmt, handlers=handlers)


def run_server(port: int = None):
    import threading
    import urllib.request
    import uvicorn

    cfg = _load_api_config()
    host    = cfg["host"]
    port    = port if port is not None else cfg["port"]
    workers = cfg["workers"]
    display_host = "localhost" if host in ("0.0.0.0", "::") else host
    print(f"Pan SORFIX  v3.0.0", flush=True)
    print(f"  API docs : http://{display_host}:{port}/docs", flush=True)
    print(f"  Health   : http://{display_host}:{port}/health", flush=True)
    print(f"  WebSocket: ws://{display_host}:{port}/ws/book/{{venue}}/{{symbol}}", flush=True)
    print(f"  Workers  : {workers}", flush=True)
    print(f"  Log file : logs/app.log  (5 MB rotating, 3 backups)", flush=True)

    def _health_check(_port):
        import time as _t, urllib.request as _ur
        _t.sleep(3)  # give uvicorn time to bind and lifespan to complete
        for attempt in range(1, 11):
            try:
                with _ur.urlopen(f"http://localhost:{_port}/health", timeout=2) as r:
                    if r.status == 200:
                        print(f"  Health check PASSED (attempt {attempt}) — server is ready", flush=True)
                        return
            except Exception:
                pass
            _t.sleep(1)
        print("  WARNING: Health check did not pass after 10s — check logs/app.log for errors", flush=True)

    threading.Thread(target=_health_check, args=(port,), daemon=True, name="HealthCheck").start()

    # workers > 1 uses uvicorn multiprocess supervisor (Linux/production).
    # workers == 1 runs in-process — no subprocess race on stdout, simpler on Windows.
    uvicorn.run(
        "api.gateway:app",
        host=host,
        port=port,
        workers=workers if workers > 1 else None,
        reload=False,
        log_level="info",
    )


def run_demo():
    """Routes sample orders across all four Pan-African venues and prints results."""
    from app_state import init_app_state
    from tools.smart_order_router import Order, OrderSide

    print("=" * 60)
    print("  Pan SORFIX  v3.0 -- Demo Mode")
    print("  Pan-African SOR: GSE | JSE | NGX | NSE")
    print("=" * 60)

    state = init_app_state(simulate=True)
    print("\nWaiting 1s for market data pipeline to populate cache...")
    time.sleep(1.0)

    orders = [
        # GSE — Ghana Stock Exchange (GHS)
        Order(symbol="GCB",      side=OrderSide.BUY,  quantity=5000,  price=5.80),
        Order(symbol="MTNGH",    side=OrderSide.SELL, quantity=10000, price=None),
        Order(symbol="GOIL",     side=OrderSide.BUY,  quantity=2000,  price=2.40),
        # JSE — Johannesburg Stock Exchange (ZAR)
        Order(symbol="MTN",      side=OrderSide.BUY,  quantity=1000,  price=148.50),
        Order(symbol="NPN",      side=OrderSide.SELL, quantity=200,   price=None),
        Order(symbol="SOL",      side=OrderSide.BUY,  quantity=500,   price=320.0),
        # NGX — Nigerian Exchange Group (NGN)
        Order(symbol="DANGCEM",  side=OrderSide.BUY,  quantity=3000,  price=680.0),
        Order(symbol="GTCO",     side=OrderSide.SELL, quantity=5000,  price=None),
        Order(symbol="ZENITHBANK",side=OrderSide.BUY, quantity=8000,  price=35.8),
        # NSE — Nairobi Securities Exchange (KES)
        Order(symbol="SAFCOM",   side=OrderSide.BUY,  quantity=4000,  price=40.5),
        Order(symbol="EABL",     side=OrderSide.SELL, quantity=1500,  price=None),
        Order(symbol="KCB",      side=OrderSide.BUY,  quantity=6000,  price=42.25),
    ]

    venue_headers = {
        "GCB": "GSE (Ghana Stock Exchange - GHS)",
        "MTN": "JSE (Johannesburg Stock Exchange - ZAR)",
        "DANGCEM": "NGX (Nigerian Exchange Group - NGN)",
        "SAFCOM": "NSE (Nairobi Securities Exchange - KES)",
    }

    try:
        for order in orders:
            if order.symbol in venue_headers:
                print(f"\n{'='*50}")
                print(f"  {venue_headers[order.symbol]}")
                print(f"{'='*50}")
            print(f"\n  ORDER: {order.side.value.upper()} {int(order.quantity)}x {order.symbol}"
                  f" @ {'MKT' if order.price is None else order.price}")
            try:
                decision = state.sor.route(order)
                print(f"  ROUTED TO: {decision.primary_venue} "
                      f"({'split' if decision.is_split else 'single'} order)")
                print(f"  LATENCY:   {decision.routing_latency_us:.1f} us")
                for i, leg in enumerate(decision.legs, 1):
                    print(f"  Leg {i}: {leg.venue} - {int(leg.quantity)}x{leg.symbol}"
                          f" @ {leg.price} {leg.currency}  "
                          f"(est. cost {leg.estimated_cost:.2f})")

                result = state.execution.execute(decision, order.side)
                print(f"  FILLED:    {int(result.total_filled)} / {int(order.quantity)}"
                      f"  ({'OK' if result.success else 'FAILED'})")
            except RuntimeError as e:
                print(f"  ERROR: {e}")

        print(f"\n{'='*50}")
        print("\nCache stats:", state.cache.stats())
        print("Pipeline:  ", state.pipeline.get_stats())
        print("Execution: ", state.execution.get_stats())
    finally:
        state.pipeline.stop()
        from app_state import reset_app_state
        for adapter in [state.gse, state.jse, state.ngx, state.nse]:
            try:
                adapter.disconnect()
            except Exception:
                pass
        reset_app_state()
    print("\nDemo complete. Run without --demo to start the API server.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pan SORFIX — Pan-African Smart Order Router")
    parser.add_argument("--demo", action="store_true", help="Run demo routing and exit")
    parser.add_argument("--port", type=int, default=None, help="API server port (default: from sor_config.yaml api.port)")
    args = parser.parse_args()

    _setup_logging()
    if args.demo:
        run_demo()
    else:
        run_server(port=args.port)
