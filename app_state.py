"""
Shared application state — singleton wiring all components together.
Call init_app_state() once at startup; get_app_state() everywhere else.
Both venues.yaml and sor_config.yaml are the single sources of truth for all
venue and routing parameters — no hardcoded values here.
"""
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from tools.order_book_cache        import ShardedOrderBookCache
from tools.fx_optimizer            import FXOptimizer
from tools.smart_order_router      import SmartOrderRouter, SORConfig, VenueConfig
from tools.market_data_pipeline    import MarketDataPipeline
from tools.execution_engine        import ExecutionEngine
from tools.fix_engine              import FIXSession
from tools.circuit_breaker         import CircuitBreaker, CircuitBreakerConfig
from tools.order_store             import OrderStore
from tools.risk_engine             import RiskEngine, RiskConfig
from tools.position_tracker        import PositionTracker
from tools.algo_engine             import AlgoEngine
from tools.db                      import OrderDB
from tools.position_ledger         import PositionLedger
import tools.admin_audit_log       as admin_audit_log
from tools.venue_adapters.nyse_adapter     import NYSEAdapter
from tools.venue_adapters.lse_adapter      import LSEAdapter
from tools.venue_adapters.hkex_adapter     import HKEXAdapter
from tools.venue_adapters.tse_adapter      import TSEAdapter
from tools.venue_adapters.sse_adapter      import SSEAdapter
from tools.venue_adapters.szse_adapter     import SZSEAdapter
from tools.venue_adapters.tadawul_adapter  import TADAWULAdapter
from tools.venue_adapters.nse_in_adapter   import NSEINAdapter
from tools.venue_adapters.euronext_adapter import EURONEXTAdapter


@dataclass
class AppState:
    cache:       ShardedOrderBookCache
    fx:          FXOptimizer
    sor:         SmartOrderRouter
    pipeline:    MarketDataPipeline
    execution:   ExecutionEngine
    order_store: OrderStore
    risk:        RiskEngine
    positions:   PositionTracker
    algo:        AlgoEngine
    db:          OrderDB
    nyse:        NYSEAdapter
    lse:         LSEAdapter
    hkex:        HKEXAdapter
    tse:         TSEAdapter
    sse:         SSEAdapter
    szse:        SZSEAdapter
    tadawul:     TADAWULAdapter
    nse_in:      NSEINAdapter
    euronext:         EURONEXTAdapter
    halted:           bool = False
    position_ledger:  PositionLedger = None


_state: Optional[AppState] = None
_init_lock = threading.Lock()


def _load_yaml(path: Path, label: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise RuntimeError(f"{label} is empty or not a YAML mapping")
        return data
    except FileNotFoundError:
        raise RuntimeError(f"{label} not found at {path}") from None
    except yaml.YAMLError as exc:
        raise RuntimeError(f"{label} is malformed YAML: {exc}") from exc


def _load_venues(raw: dict) -> dict:
    try:
        venues = {}
        for name, v in raw["venues"].items():
            venues[name] = VenueConfig(
                name=name,
                currency=v["currency"],
                taker_fee=float(v["taker_fee"]),
                latency_ms=float(v["latency_ms"]),
                enabled=bool(v["enabled"]),
            )
        return venues
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"venues.yaml is malformed: {exc}") from exc


def _validated_sor_config(r: dict) -> SORConfig:
    cfg = SORConfig(
        liquidity_weight=float(r["liquidity_weight"]),
        spread_weight=float(r["spread_weight"]),
        fee_weight=float(r["fee_weight"]),
        fx_weight=float(r["fx_weight"]),
        latency_weight=float(r["latency_weight"]),
        reliability_weight=float(r.get("reliability_weight", 0.0)),
        max_splits=int(r.get("max_order_splits", 5)),
        min_split_qty=float(r.get("min_split_quantity", 100.0)),
    )
    total = (cfg.liquidity_weight + cfg.spread_weight + cfg.fee_weight
             + cfg.fx_weight + cfg.latency_weight + cfg.reliability_weight)
    if abs(total - 1.0) > 1e-6:
        raise RuntimeError(
            f"sor_config.yaml routing weights must sum to 1.0, got {total:.6f}"
        )
    if cfg.max_splits < 1 or cfg.max_splits > 10:
        raise RuntimeError(
            f"sor_config.yaml max_order_splits must be 1–10, got {cfg.max_splits}"
        )
    if cfg.min_split_qty <= 0:
        raise RuntimeError(
            f"sor_config.yaml min_split_quantity must be > 0, got {cfg.min_split_qty}"
        )
    return cfg


def _load_sor_config(raw: dict) -> dict:
    try:
        r = raw["routing"]
        cb = raw["circuit_breaker"]
        ex = raw["execution"]
        fx = raw.get("fx_rates", {})
        md = raw.get("market_data", {})
        rk = raw.get("risk", {})
        return {
            "sor": _validated_sor_config(r),
            "cb": CircuitBreakerConfig(
                failure_threshold=int(cb["failure_threshold"]),
                success_threshold=int(cb["success_threshold"]),
                timeout_seconds=float(cb["timeout_seconds"]),
            ),
            "max_retries": int(ex["max_retries"]),
            "retry_delay_ms": float(ex["retry_delay_ms"]),
            "order_timeout_s": float(ex.get("order_timeout_seconds", 30.0)),
            "simulate": bool(ex.get("simulate", True)),
            "shard_count": int(raw.get("cache", {}).get("shard_count", 256)),
            "update_interval": float(md.get("update_interval_seconds", 0.1)),
            "fx_rates": {k: float(v) for k, v in fx.items() if k != "base_currency"},
            "fx_base": str(fx.get("base_currency", "USD")),
            "risk": RiskConfig(
                enabled=bool(rk.get("enabled", True)),
                max_order_qty=float(rk.get("max_order_qty", 1_000_000.0)),
                max_order_notional=float(rk.get("max_order_notional", 10_000_000.0)),
                price_band_pct=float(rk.get("price_band_pct", 0.05)),
                max_daily_notional=float(rk.get("max_daily_notional", 50_000_000.0)),
                max_position_qty=float(rk.get("max_position_qty", 5_000_000.0)),
            ),
        }
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"sor_config.yaml is malformed: {exc}") from exc


def init_app_state(simulate: bool = None) -> AppState:
    global _state
    with _init_lock:
        if _state is not None:
            return _state

        cfg_dir = Path(__file__).parent / "configs"
        venues_raw = _load_yaml(cfg_dir / "venues.yaml", "venues.yaml")
        sor_raw    = _load_yaml(cfg_dir / "sor_config.yaml", "sor_config.yaml")

        venues    = _load_venues(venues_raw)
        sor_cfg   = _load_sor_config(sor_raw)

        # Priority: explicit arg > SIMULATE env var > sor_config.yaml
        if simulate is None:
            _env = os.environ.get("SIMULATE", "").strip().lower()
            if _env in ("true", "1", "yes"):
                simulate = True
            elif _env in ("false", "0", "no"):
                simulate = False
        use_simulate = simulate if simulate is not None else sor_cfg["simulate"]

        cache = ShardedOrderBookCache(shard_count=sor_cfg["shard_count"])
        fx    = FXOptimizer(base_currency=sor_cfg["fx_base"])
        for ccy, rate in sor_cfg["fx_rates"].items():
            fx.update_rate(ccy, rate)

        cb_config = sor_cfg["cb"]
        circuit_breakers = {name: CircuitBreaker(name, cb_config) for name in venues}

        sor = SmartOrderRouter(
            cache=cache,
            fx_optimizer=fx,
            venues=venues,
            config=sor_cfg["sor"],
            circuit_breakers=circuit_breakers,
        )

        pipeline = MarketDataPipeline(
            cache=cache,
            update_interval=sor_cfg["update_interval"],
        )

        _sender_ids = {
            "NYSE": "BROKER_US", "LSE": "BROKER_GB", "HKEX": "BROKER_HK", "TSE": "BROKER_JP",
            "SSE": "BROKER_CN_SH", "SZSE": "BROKER_CN_SZ", "TADAWUL": "BROKER_SA",
            "NSE_IN": "BROKER_IN", "EURONEXT": "BROKER_EU",
        }
        _target_ids = {
            "NYSE": "NYSE_TRADING", "LSE": "LSE_TRADING", "HKEX": "HKEX_TRADING", "TSE": "TSE_TRADING",
            "SSE": "SSE_TRADING", "SZSE": "SZSE_TRADING", "TADAWUL": "TADAWUL_TRADING",
            "NSE_IN": "NSE_IN_TRADING", "EURONEXT": "EURONEXT_TRADING",
        }
        sessions = {
            name: FIXSession(
                sender=_sender_ids.get(name, f"BROKER_{name}"),
                target=_target_ids.get(name, f"{name}_TRADING"),
            )
            for name in venues
        }

        execution = ExecutionEngine(
            sessions=sessions,
            circuit_breakers=circuit_breakers,
            max_retries=sor_cfg["max_retries"],
            retry_delay_ms=sor_cfg["retry_delay_ms"],
            order_timeout_s=sor_cfg["order_timeout_s"],
            simulate=use_simulate,
        )

        risk_engine = RiskEngine(config=sor_cfg["risk"])
        positions   = PositionTracker()
        order_db    = OrderDB()

        adapters_connected = []
        try:
            nyse = NYSEAdapter()
            nyse.connect()
            adapters_connected.append(nyse)

            lse = LSEAdapter()
            lse.connect()
            adapters_connected.append(lse)

            hkex = HKEXAdapter()
            hkex.connect()
            adapters_connected.append(hkex)

            tse = TSEAdapter()
            tse.connect()
            adapters_connected.append(tse)

            sse = SSEAdapter();     sse.connect();     adapters_connected.append(sse)
            szse = SZSEAdapter();   szse.connect();    adapters_connected.append(szse)
            tadawul = TADAWULAdapter(); tadawul.connect(); adapters_connected.append(tadawul)
            nse_in = NSEINAdapter(); nse_in.connect();  adapters_connected.append(nse_in)
            euronext = EURONEXTAdapter(); euronext.connect(); adapters_connected.append(euronext)

            pipeline.start()
        except Exception:
            for adapter in reversed(adapters_connected):
                try:
                    adapter.disconnect()
                except Exception:
                    pass
            raise

        # AlgoEngine needs a submit function wired after all components exist.
        # We use a closure that is replaced once _state is set below.
        _order_store = OrderStore()

        def _algo_submit(symbol, side, quantity, price, base_currency):
            from tools.smart_order_router import Order, OrderSide
            import time as _time
            _s = get_app_state()
            order = Order(
                symbol=symbol, side=OrderSide(side),
                quantity=quantity, price=price, base_currency=base_currency,
            )
            decision = _s.sor.route(order)
            result   = _s.execution.execute(decision, order.side)
            fill_ratio = result.total_filled / decision.total_quantity if decision.total_quantity > 0 else 0.0
            vwap = result.total_cost / result.total_filled if result.total_filled > 0 else None
            from api.models import (
                OrderResponse, ExecutionReportResponse,
                RoutingDecisionResponse, RoutingLegResponse, VenueScoreResponse,
            )
            routing = RoutingDecisionResponse(
                order_id=decision.order_id, symbol=decision.symbol,
                total_quantity=decision.total_quantity, primary_venue=decision.primary_venue,
                legs=[RoutingLegResponse(venue=l.venue, symbol=l.symbol, quantity=l.quantity,
                                         price=l.price, currency=l.currency,
                                         estimated_cost=l.estimated_cost) for l in decision.legs],
                routing_latency_us=decision.routing_latency_us,
                is_split=decision.is_split, timestamp=decision.timestamp,
                venue_scores=[VenueScoreResponse(venue=s.venue, score=round(s.total,6),
                               liquidity=round(s.liquidity,6), spread=round(s.spread,6),
                               fee=round(s.fee,6), fx_cost=round(s.fx_cost,6),
                               latency=round(s.latency,6), available_qty=s.available_qty,
                               reliability=round(s.reliability,6))
                               for s in decision.venue_scores],
            )
            resp = OrderResponse(
                order_id=decision.order_id, side=side,
                routing=routing,
                executions=[ExecutionReportResponse(
                    leg_venue=r.leg.venue, status=r.status.value,
                    filled_qty=r.filled_qty,
                    avg_price=r.avg_price if r.filled_qty > 0 else None,
                    message=r.message, attempts=r.attempts,
                ) for r in result.reports],
                total_filled=result.total_filled, total_cost=result.total_cost,
                success=result.success, fill_ratio=round(fill_ratio, 6),
                vwap=round(vwap, 6) if vwap is not None else None,
                timestamp=_time.time(),
            )
            data = resp.model_dump()
            _s.order_store.save(decision.order_id, data)
            _s.db.save(decision.order_id, data)
            if result.total_filled > 0:
                _s.positions.record_fill(symbol, side, result.total_filled,
                                         result.total_cost / result.total_filled)
                _s.risk.record_fill(result.total_filled, result.total_cost / result.total_filled)
            return {"order_id": decision.order_id,
                    "total_filled": result.total_filled,
                    "total_cost": result.total_cost,
                    "success": result.success}

        algo_engine = AlgoEngine(submit_fn=_algo_submit)

        _state = AppState(
            cache=cache,
            fx=fx,
            sor=sor,
            pipeline=pipeline,
            execution=execution,
            order_store=_order_store,
            risk=risk_engine,
            positions=positions,
            algo=algo_engine,
            db=order_db,
            nyse=nyse,
            lse=lse,
            hkex=hkex,
            tse=tse,
            sse=sse,
            szse=szse,
            tadawul=tadawul,
            nse_in=nse_in,
            euronext=euronext,
        )
        _state.position_ledger = PositionLedger()
        admin_audit_log.init()
        return _state


def get_app_state() -> AppState:
    if _state is None:
        raise RuntimeError("App state not initialized — call init_app_state() first")
    return _state


def reset_app_state():
    """Clear the singleton so init_app_state() creates fresh state on next call.
    Must be called after pipeline.stop() and all adapter disconnects to avoid orphaned threads."""
    global _state
    with _init_lock:
        _state = None
