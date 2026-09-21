"""
Execution engine — sends FIX orders per routing decision, manages retries with idempotency.
Parallel leg execution: all legs of a split order fire simultaneously in separate threads.
"""
import collections
import logging
import math
import random
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

from tools.fix_engine import FIXSession
from tools.smart_order_router import RoutingDecision, RoutingLeg, OrderSide
from tools.circuit_breaker import CircuitBreaker
from tools.monitoring import metrics

logger = logging.getLogger("execution_engine")


class ExecutionStatus(Enum):
    PENDING   = "pending"
    SUBMITTED = "submitted"
    FILLED    = "filled"
    PARTIAL   = "partial"
    REJECTED  = "rejected"
    CANCELLED = "cancelled"
    FAILED    = "failed"


_TERMINAL_STATUSES = frozenset({ExecutionStatus.REJECTED, ExecutionStatus.FAILED})


@dataclass
class ExecutionReport:
    order_id:   str
    leg:        RoutingLeg
    status:     ExecutionStatus
    filled_qty: float          = 0.0
    avg_price:  Optional[float] = None  # None means unfilled; 0.0 is a valid price
    message:    str            = ""
    attempts:   int            = 0
    latency_ms: float          = 0.0
    timestamp:  float          = field(default_factory=time.time)


@dataclass
class ExecutionResult:
    decision:     RoutingDecision
    reports:      List[ExecutionReport]
    total_filled: float = 0.0
    total_cost:   float = 0.0
    success:      bool  = False


class ExecutionEngine:
    def __init__(
        self,
        sessions: Dict[str, FIXSession],
        circuit_breakers: Dict[str, CircuitBreaker],
        max_retries: int       = 3,
        retry_delay_ms: float  = 100.0,
        simulate: bool         = True,
        order_timeout_s: float = 30.0,
    ):
        self.sessions         = sessions
        self.circuit_breakers = circuit_breakers
        self.max_retries      = max_retries
        self.retry_delay_s    = retry_delay_ms / 1_000
        self.simulate         = simulate
        self.order_timeout_s  = order_timeout_s

        # Bounded LRU idempotency store — prevents unbounded memory growth.
        self._executed: collections.OrderedDict = collections.OrderedDict()
        self._idem_maxsize = 50_000
        self._lock         = threading.Lock()

        # Metrics counters
        self._exec_count    = 0
        self._fail_count    = 0
        self._total_filled  = 0.0
        self._total_latency_ms = 0.0  # cumulative, for avg latency

    # ------------------------------------------------------------------ #
    # Idempotency cache                                                    #
    # ------------------------------------------------------------------ #

    def _idem_key(self, order_id: str, venue: str) -> str:
        return f"{order_id}:{venue}"

    def _idem_set(self, key: str, report: ExecutionReport):
        """Write to idempotency cache; evict oldest entry when at capacity."""
        if len(self._executed) >= self._idem_maxsize:
            self._executed.popitem(last=False)
        self._executed[key] = report

    # ------------------------------------------------------------------ #
    # Simulation                                                           #
    # ------------------------------------------------------------------ #

    # Venue-specific latency profiles (ms): realistic round-trip per exchange
    _VENUE_LATENCY = {
        "JSE": (1.5, 3.5),   # Johannesburg — lowest latency
        "GSE": (3.0, 7.0),   # Ghana
        "NGX": (4.0, 9.0),   # Nigeria
        "NSE": (5.0, 10.0),  # Nairobi — highest latency
    }

    def _simulate_leg(self, leg: RoutingLeg, order_id: str, side: OrderSide) -> ExecutionReport:
        """Simulate a single-leg FIX execution: venue-aware latency, context-aware fill, ISR slippage model."""
        if leg.price is None:
            return ExecutionReport(
                order_id=order_id, leg=leg,
                status=ExecutionStatus.REJECTED,
                message="No market price available — order book empty at routing time",
                attempts=1,
            )

        # Venue-aware round-trip latency
        lo, hi = self._VENUE_LATENCY.get(leg.venue, (2.0, 8.0))
        start = time.perf_counter()
        time.sleep(random.uniform(lo / 1_000, hi / 1_000))
        latency_ms = (time.perf_counter() - start) * 1_000

        # Low flat rejection rate — 1.5% — realistic for a well-connected electronic venue.
        if random.random() < 0.015:
            return ExecutionReport(
                order_id=order_id, leg=leg,
                status=ExecutionStatus.REJECTED,
                message="Exchange rejection — order failed pre-trade check",
                latency_ms=latency_ms,
                attempts=1,
            )

        # High fill rate: Gaussian centred at 99.8%, std 0.1%, floored at 99%.
        # Nearly all orders fully fill; rare PARTIAL only on extreme book conditions.
        fill_pct = min(1.0, max(0.99, random.gauss(0.998, 0.001)))
        filled   = round(leg.quantity * fill_pct)

        # Slippage: 0.5–1.5 bps adverse (buy fills slightly above, sell slightly below).
        slippage_bps = random.uniform(0.5, 1.5)
        if side == OrderSide.BUY:
            fill_price = round(leg.price * (1.0 + slippage_bps / 10_000), 6)
        else:
            fill_price = round(leg.price * (1.0 - slippage_bps / 10_000), 6)

        # FILLED if ≥99.5% executed (virtually always), PARTIAL only for the rare remainder
        status = ExecutionStatus.FILLED if fill_pct >= 0.995 else ExecutionStatus.PARTIAL
        label  = "filled" if status == ExecutionStatus.FILLED else "partial fill"
        return ExecutionReport(
            order_id=order_id, leg=leg,
            status=status,
            filled_qty=filled,
            avg_price=fill_price,
            message=f"Simulated {label} ({fill_pct*100:.2f}%) @ {fill_price:.4f}  slippage={slippage_bps:.2f}bps",
            latency_ms=latency_ms,
            attempts=1,
        )

    # ------------------------------------------------------------------ #
    # Leg execution with retry + circuit breaker                           #
    # ------------------------------------------------------------------ #

    def _execute_leg(self, leg: RoutingLeg, order_id: str, side: OrderSide) -> ExecutionReport:
        idem_key = self._idem_key(order_id, leg.venue)

        # Idempotency check — return cached result for duplicate calls.
        with self._lock:
            if idem_key in self._executed:
                logger.debug("Idempotency hit: %s", idem_key)
                return self._executed[idem_key]

        # Fast-path: no price means the order book was empty; no retry can fix this.
        if self.simulate and leg.price is None:  # side irrelevant here — always a reject
            report = ExecutionReport(
                order_id=order_id, leg=leg,
                status=ExecutionStatus.REJECTED,
                message="No market price available — order book empty at routing time",
                attempts=1,
            )
            cb = self.circuit_breakers.get(leg.venue)
            if cb:
                cb.record_failure()
            with self._lock:
                self._fail_count += 1
                self._idem_set(idem_key, report)
            logger.warning("Leg %s@%s rejected: no price", order_id, leg.venue)
            return report

        cb           = self.circuit_breakers.get(leg.venue)
        last_err     = RuntimeError(f"Circuit breaker OPEN for {leg.venue} — all retries blocked")
        last_report: Optional[ExecutionReport] = None
        attempt      = 0

        for attempt in range(1, self.max_retries + 1):
            if cb and not cb.allow():
                logger.warning("Leg %s@%s: CB open, aborting after %d attempt(s)", order_id, leg.venue, attempt - 1)
                break

            try:
                if self.simulate:
                    report = self._simulate_leg(leg, order_id, side)
                else:
                    session = self.sessions.get(leg.venue)
                    if not session:
                        raise RuntimeError(f"No FIX session for {leg.venue}")
                    # TODO: build FIX NewOrderSingle, write to TCP socket, await ExecutionReport (35=8)
                    raise NotImplementedError("Live FIX socket not wired — set simulate=True")

                report.attempts = attempt

                if cb:
                    if report.status in _TERMINAL_STATUSES:
                        cb.record_failure()
                    else:
                        cb.record_success()

                # Success — cache and return; never retry a filled order.
                if report.status not in _TERMINAL_STATUSES:
                    with self._lock:
                        self._idem_set(idem_key, report)
                        self._exec_count += 1
                        self._total_filled  += report.filled_qty
                        self._total_latency_ms += report.latency_ms
                    logger.info(
                        "Leg %s@%s: %s filled=%.0f avg=%.4f lat=%.1fms (attempt %d)",
                        order_id, leg.venue, report.status.value,
                        report.filled_qty, report.avg_price or 0, report.latency_ms, attempt,
                    )
                    return report

                last_report = report
                logger.debug(
                    "Leg %s@%s attempt %d/%d rejected: %s",
                    order_id, leg.venue, attempt, self.max_retries, report.message,
                )

            except Exception as exc:
                last_err = exc
                logger.warning("Leg %s@%s attempt %d/%d exception: %s", order_id, leg.venue, attempt, self.max_retries, exc)
                if cb:
                    cb.record_failure()

            # Exponential backoff with full jitter before next attempt.
            if attempt < self.max_retries:
                backoff = min(self.retry_delay_s * (2 ** (attempt - 1)), 5.0)
                jitter  = random.uniform(0, backoff)
                time.sleep(jitter)

        # All retries exhausted.
        report = last_report or ExecutionReport(
            order_id=order_id, leg=leg,
            status=ExecutionStatus.FAILED,
            message=str(last_err),
            attempts=max(attempt, 1),
        )
        report.attempts = max(attempt, 1)
        with self._lock:
            self._fail_count += 1
            self._idem_set(idem_key, report)
        logger.warning(
            "Leg %s@%s exhausted %d retries: %s",
            order_id, leg.venue, report.attempts, report.message,
        )
        return report

    # ------------------------------------------------------------------ #
    # Parallel execution across all legs                                   #
    # ------------------------------------------------------------------ #

    def execute(self, decision: RoutingDecision, side: OrderSide) -> ExecutionResult:
        n = len(decision.legs)
        slots: List[Optional[ExecutionReport]] = [None] * n
        slot_lock = threading.Lock()

        def run_leg(idx: int, leg: RoutingLeg):
            r = self._execute_leg(leg, decision.order_id, side)
            with slot_lock:
                if slots[idx] is None:
                    slots[idx] = r

        threads = [
            threading.Thread(
                target=run_leg,
                args=(i, leg),
                name=f"exec-{decision.order_id[:8]}-{leg.venue}",
                daemon=True,
            )
            for i, leg in enumerate(decision.legs)
        ]

        deadline = time.monotonic() + self.order_timeout_s
        for t in threads:
            t.start()

        # Join threads against a shared wall-clock deadline so a slow first leg
        # doesn't eat into the budget of subsequent legs.
        for i, (t, leg) in enumerate(zip(threads, decision.legs)):
            remaining = max(0.0, deadline - time.monotonic())
            t.join(timeout=remaining)
            with slot_lock:
                if slots[i] is None:
                    slots[i] = ExecutionReport(
                        order_id=decision.order_id,
                        leg=leg,
                        status=ExecutionStatus.FAILED,
                        message=f"Execution timed out after {self.order_timeout_s:.0f}s",
                        attempts=self.max_retries,
                    )
                    with self._lock:
                        self._fail_count += 1
                    logger.error("Leg %s@%s timed out", decision.order_id, leg.venue)

        reports: List[ExecutionReport] = [s for s in slots if s is not None]

        total_filled = sum(r.filled_qty for r in reports)
        total_cost   = sum(r.filled_qty * (r.avg_price or 0.0) for r in reports)
        success      = total_filled > 0

        # Emit metrics
        for r in reports:
            metrics.inc("execution_orders_total", status=r.status.value, venue=r.leg.venue)
            if r.filled_qty > 0:
                metrics.observe("execution_fill_qty", r.filled_qty, venue=r.leg.venue)
            if r.latency_ms > 0:
                metrics.observe("execution_latency_ms", r.latency_ms, venue=r.leg.venue)
        with self._lock:
            metrics.set_gauge("execution_idempotency_cache_size", len(self._executed))

        logger.info(
            "Order %s: %d leg(s), filled=%.0f/%.0f, cost=%.2f, success=%s",
            decision.order_id, n, total_filled, decision.total_quantity, total_cost, success,
        )

        return ExecutionResult(
            decision=decision,
            reports=reports,
            total_filled=total_filled,
            total_cost=total_cost,
            success=success,
        )

    # ------------------------------------------------------------------ #
    # Observability                                                        #
    # ------------------------------------------------------------------ #

    def get_stats(self) -> dict:
        with self._lock:
            total      = self._exec_count + self._fail_count
            fill_rate  = self._exec_count / total if total > 0 else 0.0
            avg_lat    = (self._total_latency_ms / self._exec_count
                          if self._exec_count > 0 else 0.0)
            return {
                "executions":             self._exec_count,
                "failures":               self._fail_count,
                "total_attempts":         total,
                "fill_rate":              round(fill_rate, 4),
                "total_filled_qty":       round(self._total_filled, 2),
                "avg_latency_ms":         round(avg_lat, 2),
                "idempotency_cache_size": len(self._executed),
                "simulate":               self.simulate,
            }
