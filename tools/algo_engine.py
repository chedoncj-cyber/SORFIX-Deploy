"""
Algorithmic execution engine — TWAP and VWAP slice-based order execution.
Each algo order runs in its own daemon thread, slicing the parent order
into child orders submitted through the SmartOrderRouter.
"""
import logging
import math
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional

logger = logging.getLogger("algo_engine")


class AlgoType(str, Enum):
    TWAP = "twap"
    VWAP = "vwap"


class AlgoStatus(str, Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED    = "failed"


@dataclass
class AlgoOrder:
    algo_id: str
    algo_type: AlgoType
    symbol: str
    side: str
    total_qty: float
    price: Optional[float]
    base_currency: str
    duration_seconds: float       # how long to spread the execution
    slices: int                   # how many child orders
    status: AlgoStatus = AlgoStatus.PENDING
    submitted_qty: float = 0.0
    filled_qty: float = 0.0
    total_cost: float = 0.0
    start_ts: Optional[float] = None
    end_ts: Optional[float] = None
    child_orders: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "algo_id": self.algo_id,
            "algo_type": self.algo_type.value,
            "symbol": self.symbol,
            "side": self.side,
            "total_qty": self.total_qty,
            "price": self.price,
            "base_currency": self.base_currency,
            "duration_seconds": self.duration_seconds,
            "slices": self.slices,
            "status": self.status.value,
            "submitted_qty": round(self.submitted_qty, 6),
            "filled_qty": round(self.filled_qty, 6),
            "total_cost": round(self.total_cost, 6),
            "vwap": round(self.total_cost / self.filled_qty, 6) if self.filled_qty > 0 else None,
            "fill_ratio": round(self.filled_qty / self.total_qty, 6) if self.total_qty > 0 else 0.0,
            "start_ts": self.start_ts,
            "end_ts": self.end_ts,
            "child_orders": self.child_orders,
            "error": self.error,
        }


SubmitFn = Callable[[str, str, float, Optional[float], str], dict]


class AlgoEngine:
    """
    Runs TWAP/VWAP algo orders in background threads.
    submit_fn must be a callable that submits a single child order and returns
    a dict with keys: order_id, total_filled, total_cost, success.
    """

    def __init__(self, submit_fn: SubmitFn):
        self._submit_fn = submit_fn
        self._lock = threading.Lock()
        self._orders: Dict[str, AlgoOrder] = {}
        self._stop_events: Dict[str, threading.Event] = {}

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def submit_twap(
        self,
        symbol: str,
        side: str,
        total_qty: float,
        duration_seconds: float,
        slices: int,
        price: Optional[float] = None,
        base_currency: str = "USD",
    ) -> AlgoOrder:
        return self._create_and_start(
            AlgoType.TWAP, symbol, side, total_qty,
            price, base_currency, duration_seconds, slices,
        )

    def submit_vwap(
        self,
        symbol: str,
        side: str,
        total_qty: float,
        duration_seconds: float,
        slices: int,
        price: Optional[float] = None,
        base_currency: str = "USD",
    ) -> AlgoOrder:
        return self._create_and_start(
            AlgoType.VWAP, symbol, side, total_qty,
            price, base_currency, duration_seconds, slices,
        )

    def cancel(self, algo_id: str) -> bool:
        """Signal a running algo to stop after its current slice."""
        with self._lock:
            order = self._orders.get(algo_id)
            stop  = self._stop_events.get(algo_id)
            if order is None:
                return False
            if order.status not in (AlgoStatus.PENDING, AlgoStatus.RUNNING):
                return False
            # Set status inside the lock so _run_algo cannot race to set COMPLETED.
            order.status = AlgoStatus.CANCELLED
            order.end_ts = time.time()
        if stop:
            stop.set()
        logger.info("Algo %s cancellation requested", algo_id)
        return True

    def get(self, algo_id: str) -> Optional[AlgoOrder]:
        with self._lock:
            return self._orders.get(algo_id)

    def get_all(self) -> list:
        with self._lock:
            return [o.to_dict() for o in self._orders.values()]

    def get_active(self) -> list:
        with self._lock:
            return [
                o.to_dict() for o in self._orders.values()
                if o.status in (AlgoStatus.PENDING, AlgoStatus.RUNNING)
            ]

    # ------------------------------------------------------------------ #
    # Internal                                                             #
    # ------------------------------------------------------------------ #

    def _create_and_start(
        self,
        algo_type: AlgoType,
        symbol: str,
        side: str,
        total_qty: float,
        price: Optional[float],
        base_currency: str,
        duration_seconds: float,
        slices: int,
    ) -> AlgoOrder:
        algo_id = f"{algo_type.value.upper()}-{uuid.uuid4().hex[:8].upper()}"
        stop    = threading.Event()
        order   = AlgoOrder(
            algo_id=algo_id,
            algo_type=algo_type,
            symbol=symbol,
            side=side,
            total_qty=total_qty,
            price=price,
            base_currency=base_currency,
            duration_seconds=duration_seconds,
            slices=slices,
        )
        with self._lock:
            self._orders[algo_id] = order
            self._stop_events[algo_id] = stop

        t = threading.Thread(
            target=self._run_algo,
            args=(order, stop),
            name=f"algo-{algo_id}",
            daemon=True,
        )
        t.start()
        logger.info(
            "Algo %s started: %s %s %.0f qty / %ds / %d slices",
            algo_id, algo_type.value.upper(), symbol, total_qty, duration_seconds, slices,
        )
        return order

    def _run_algo(self, order: AlgoOrder, stop: threading.Event):
        order.status  = AlgoStatus.RUNNING
        order.start_ts = time.time()
        interval = order.duration_seconds / order.slices
        slice_qty = order.total_qty / order.slices

        try:
            for i in range(order.slices):
                if stop.is_set():
                    break

                qty = slice_qty
                if i == order.slices - 1:
                    # Last slice — clean up any rounding remainder
                    qty = order.total_qty - order.submitted_qty

                if qty <= 0:
                    break

                # VWAP: skew slice size by simulated volume profile (bell curve peak midday).
                # Skip weight on the last slice — use exact remaining qty so total fills completely.
                if order.algo_type == AlgoType.VWAP and i < order.slices - 1:
                    progress = i / max(order.slices - 1, 1)
                    weight = math.exp(-8 * (progress - 0.5) ** 2) + 0.2
                    qty = min(qty * weight, order.total_qty - order.submitted_qty)
                    if qty <= 0:
                        break

                try:
                    result = self._submit_fn(
                        order.symbol, order.side, qty,
                        order.price, order.base_currency,
                    )
                    child_id = result.get("order_id", f"{order.algo_id}-{i}")
                    order.child_orders.append(child_id)
                    order.submitted_qty += qty
                    order.filled_qty += result.get("total_filled", 0.0)
                    order.total_cost  += result.get("total_cost", 0.0)
                    logger.info(
                        "Algo %s slice %d/%d: child=%s filled=%.0f",
                        order.algo_id, i + 1, order.slices,
                        child_id, result.get("total_filled", 0.0),
                    )
                except Exception as exc:
                    logger.warning("Algo %s slice %d error: %s", order.algo_id, i + 1, exc)

                if i < order.slices - 1:
                    stop.wait(timeout=interval)

            with self._lock:
                # Only transition to COMPLETED if cancel() hasn't already set CANCELLED.
                if order.status not in (AlgoStatus.CANCELLED,):
                    order.status = AlgoStatus.COMPLETED
                    order.end_ts = time.time()
            logger.info(
                "Algo %s %s: filled=%.0f/%.0f cost=%.2f",
                order.algo_id, order.status.value,
                order.filled_qty, order.total_qty, order.total_cost,
            )
        except Exception as exc:
            order.status = AlgoStatus.FAILED
            order.error  = str(exc)
            order.end_ts = time.time()
            logger.exception("Algo %s failed", order.algo_id)
