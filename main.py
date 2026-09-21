#!/usr/bin/env python3
"""
World SORFIX  v3.0
Global Low-Latency Smart Order Router
9 Exchanges: NYSE · LSE · HKEX · TSE · SSE · SZSE · TADAWUL · NSE_IN · EURONEXT

Usage:
  python main.py                    # Start API server on port 9091
  python main.py --demo             # Print a demo routing decision and exit
  python main.py --port 9091        # Custom port
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
    print(f"World SORFIX  v3.0.0", flush=True)
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
    """Routes sample orders across all four global venues and prints results."""
    from app_state import init_app_state
    from tools.smart_order_router import Order, OrderSide

    print("=" * 60)
    print("  World SORFIX  v3.0 -- Demo Mode")
    print("  Global SOR: NYSE | LSE | HKEX | TSE | SSE | SZSE | TADAWUL | NSE_IN | EURONEXT")
    print("=" * 60)

    state = init_app_state(simulate=True)
    print("\nWaiting 1s for market data pipeline to populate cache...")
    time.sleep(1.0)

    orders = [
        # NYSE — New York Stock Exchange (USD)
        Order(symbol="AAPL",       side=OrderSide.BUY,  quantity=500,   price=189.50),
        Order(symbol="NVDA",       side=OrderSide.SELL, quantity=200,   price=None),
        Order(symbol="JPM",        side=OrderSide.BUY,  quantity=1000,  price=198.70),
        # LSE — London Stock Exchange (GBP)
        Order(symbol="SHEL",       side=OrderSide.BUY,  quantity=2000,  price=27.82),
        Order(symbol="AZN",        side=OrderSide.SELL, quantity=500,   price=None),
        Order(symbol="HSBA",       side=OrderSide.BUY,  quantity=5000,  price=7.24),
        # HKEX — Hong Kong Exchanges (HKD)
        Order(symbol="TENCENT",    side=OrderSide.BUY,  quantity=1000,  price=358.40),
        Order(symbol="ALIBABA",    side=OrderSide.SELL, quantity=2000,  price=None),
        Order(symbol="AIA",        side=OrderSide.BUY,  quantity=3000,  price=52.80),
        # TSE — Tokyo Stock Exchange (JPY)
        Order(symbol="TOYOTA",     side=OrderSide.BUY,  quantity=500,   price=3420.0),
        Order(symbol="SONY",       side=OrderSide.SELL, quantity=300,   price=None),
        Order(symbol="NINTENDO",   side=OrderSide.BUY,  quantity=200,   price=7840.0),
        # SSE — Shanghai Stock Exchange (CNY)
        Order(symbol="ICBC",       side=OrderSide.BUY,  quantity=5000,  price=5.42),
        Order(symbol="PETROCHINA", side=OrderSide.SELL, quantity=3000,  price=None),
        # SZSE — Shenzhen Stock Exchange (CNY)
        Order(symbol="BYDCO",      side=OrderSide.BUY,  quantity=500,   price=278.50),
        Order(symbol="WULIANGYE",  side=OrderSide.SELL, quantity=200,   price=None),
        # TADAWUL — Saudi Exchange (SAR)
        Order(symbol="ARAMCO",     side=OrderSide.BUY,  quantity=1000,  price=29.80),
        Order(symbol="SABIC",      side=OrderSide.SELL, quantity=500,   price=None),
        # NSE_IN — National Stock Exchange India (INR)
        Order(symbol="RELIANCE",   side=OrderSide.BUY,  quantity=200,   price=2840.0),
        Order(symbol="TCS",        side=OrderSide.SELL, quantity=100,   price=None),
        # EURONEXT — Euronext (EUR)
        Order(symbol="LVMH",       side=OrderSide.BUY,  quantity=50,    price=742.0),
        Order(symbol="TOTALENERGIES", side=OrderSide.SELL, quantity=300, price=None),
    ]

    venue_headers = {
        "AAPL":         "NYSE (New York Stock Exchange - USD)",
        "SHEL":         "LSE (London Stock Exchange - GBP)",
        "TENCENT":      "HKEX (Hong Kong Exchanges - HKD)",
        "TOYOTA":       "TSE (Tokyo Stock Exchange - JPY)",
        "ICBC":         "SSE (Shanghai Stock Exchange - CNY)",
        "BYDCO":        "SZSE (Shenzhen Stock Exchange - CNY)",
        "ARAMCO":       "TADAWUL (Saudi Exchange - SAR)",
        "RELIANCE":     "NSE_IN (National Stock Exchange India - INR)",
        "LVMH":         "EURONEXT (Euronext - EUR)",
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
        for adapter in [state.nyse, state.lse, state.hkex, state.tse,
                        state.sse, state.szse, state.tadawul, state.nse_in, state.euronext]:
            try:
                adapter.disconnect()
            except Exception:
                pass
        reset_app_state()
    print("\nDemo complete. Run without --demo to start the API server.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="World SORFIX — Global Smart Order Router")
    parser.add_argument("--demo", action="store_true", help="Run demo routing and exit")
    parser.add_argument("--port", type=int, default=None, help="API server port (default: from sor_config.yaml api.port)")
    args = parser.parse_args()

    _setup_logging()
    if args.demo:
        run_demo()
    else:
        run_server(port=args.port)
