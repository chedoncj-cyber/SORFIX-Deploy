"""
Smart Order Router — core routing logic.
Scores venues using weighted factors and splits orders to minimize cost + latency.
Six scoring dimensions: liquidity 28%, spread 18%, fee 16%, FX 18%, latency 10%, reliability 10%.
Weights are configured in configs/sor_config.yaml and must sum to 1.0.
"""
import math
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

from tools.order_book_cache import ShardedOrderBookCache, OrderBook
from tools.fx_optimizer import FXOptimizer
from tools.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from tools.monitoring import metrics


class OrderSide(Enum):
    BUY  = "buy"
    SELL = "sell"


@dataclass
class Order:
    symbol: str
    side: OrderSide
    quantity: float
    price: Optional[float] = None
    client_order_id: str = field(default_factory=lambda: uuid.uuid4().hex.upper())
    base_currency: str = "USD"
    max_splits: int = 5
    min_split_qty: float = 100.0


@dataclass
class VenueScore:
    venue: str
    total: float
    liquidity: float
    spread: float
    fee: float
    fx_cost: float
    latency: float
    available_qty: float
    reliability: float = 1.0


@dataclass
class RoutingLeg:
    venue: str
    symbol: str
    quantity: float
    price: Optional[float]
    currency: str
    estimated_cost: float


@dataclass
class RoutingDecision:
    order_id: str
    symbol: str
    total_quantity: float
    legs: List[RoutingLeg]
    primary_venue: str
    routing_latency_us: float
    timestamp: float = field(default_factory=time.time)
    venue_scores: List[VenueScore] = field(default_factory=list)

    @property
    def is_split(self) -> bool:
        return len(self.legs) > 1


@dataclass
class SORConfig:
    liquidity_weight:   float = 0.28
    spread_weight:      float = 0.18
    fee_weight:         float = 0.16
    fx_weight:          float = 0.18
    latency_weight:     float = 0.10
    reliability_weight: float = 0.10
    max_splits:         int   = 5
    min_split_qty:      float = 100.0


@dataclass
class VenueConfig:
    name: str
    currency: str
    taker_fee: float
    latency_ms: float
    enabled: bool = True


class SmartOrderRouter:
    def __init__(
        self,
        cache: ShardedOrderBookCache,
        fx_optimizer: FXOptimizer,
        venues: Dict[str, VenueConfig],
        config: SORConfig = None,
        circuit_breakers: Dict[str, "CircuitBreaker"] = None,
    ):
        self.cache = cache
        self.fx = fx_optimizer
        self.venues = venues
        self.config = config or SORConfig()
        self.circuit_breakers: Dict[str, CircuitBreaker] = (
            circuit_breakers if circuit_breakers is not None
            else {name: CircuitBreaker(name) for name in venues}
        )

    def _score_venue(self, order: Order, venue_name: str, book: OrderBook) -> VenueScore:
        venue = self.venues[venue_name]
        cfg   = self.config

        # 1. Side-aware liquidity: consume ask depth for buys, bid depth for sells.
        #    5 levels captures realistic sweep depth better than 3.
        if order.side == OrderSide.BUY:
            avail = sum(lvl.quantity for lvl in book.asks[:5])
        else:
            avail = sum(lvl.quantity for lvl in book.bids[:5])
        avail = max(avail, 1.0)

        # Market impact: sqrt participation model with stronger coefficient.
        participation = order.quantity / avail
        impact_penalty = min(0.45, 0.20 * math.sqrt(participation))
        liquidity = max(0.0, min(1.0, avail / max(order.quantity, 1.0)) - impact_penalty)

        # 2. Spread: exponential decay eliminates the hard 5% cliff.
        #    10bps → 0.90, 50bps → 0.61, 200bps → 0.14
        spread_bps = (book.spread * 10_000) if book.spread is not None else 300.0
        spread = math.exp(-spread_bps / 100.0)

        # 3. Fee: linear, calibrated against 50bps ceiling (unchanged — well-calibrated).
        fee = max(0.0, 1.0 - venue.taker_fee / 0.005)

        # 4. FX cost: per-pair costs (ZAR 8bps < GHS 12bps < KES 15bps < NGN 20bps),
        #    normalized against 30bps worst-case so same-currency always scores 1.0.
        fx_raw  = self.fx.get_conversion_cost(order.base_currency, venue.currency)
        fx_cost = max(0.0, 1.0 - fx_raw / self.fx.WORST_CASE_COST)

        # 5. Latency: exponential decay gives log-scale effect.
        #    2ms → 0.90, 8ms → 0.67, 15ms → 0.47 — 4x latency is now meaningfully penalized.
        latency = math.exp(-venue.latency_ms / 20.0)

        # 6. Reliability: recent circuit-breaker failure count depresses score.
        #    Each failure reduces by 15%, floor at 0.3 (venue still usable, just penalized).
        cb = self.circuit_breakers.get(venue_name)
        if cb:
            stats    = cb.get_stats()
            failures = stats.get("failure_count", 0)
            reliability = max(0.3, 1.0 - failures * 0.15)
        else:
            reliability = 1.0

        # Book staleness multiplier: penalize stale order book data (10s half-life).
        # Fresh books (< 1s old) are negligibly penalized; a 30s-stale book scores ~0.05.
        if book.last_update_ns > 0:
            age_s = max(0.0, (time.perf_counter_ns() - book.last_update_ns) / 1e9)
            staleness_mult = math.exp(-age_s / 10.0)
        else:
            staleness_mult = 0.8

        total = (
            liquidity   * cfg.liquidity_weight    +
            spread      * cfg.spread_weight       +
            fee         * cfg.fee_weight          +
            fx_cost     * cfg.fx_weight           +
            latency     * cfg.latency_weight      +
            reliability * cfg.reliability_weight
        ) * staleness_mult

        return VenueScore(
            venue=venue_name,
            total=total,
            liquidity=liquidity,
            spread=spread,
            fee=fee,
            fx_cost=fx_cost,
            latency=latency,
            available_qty=avail,
            reliability=reliability,
        )

    def route(self, order: Order) -> RoutingDecision:
        if order.quantity <= 0:
            raise RuntimeError(f"Order quantity must be positive, got {order.quantity}")
        start_ns = time.perf_counter_ns()

        scored: List[VenueScore] = []
        for venue_name, venue_cfg in self.venues.items():
            if not venue_cfg.enabled:
                continue
            cb = self.circuit_breakers.get(venue_name)
            if cb and not cb.allow():
                continue
            book = self.cache.get(venue_name, order.symbol)
            if book is None:
                continue
            scored.append(self._score_venue(order, venue_name, book))

        if not scored:
            enabled = [n for n, v in self.venues.items() if v.enabled]
            if not enabled:
                raise RuntimeError("No venues enabled — check configs/venues.yaml")
            # Distinguish: no book yet (pipeline warming up) vs unknown symbol
            known_symbols = self.cache.get_known_symbols()
            if not known_symbols:
                raise RuntimeError(
                    "No order book data yet — market data pipeline is warming up, retry in 1-2 seconds"
                )
            if order.symbol not in known_symbols:
                raise RuntimeError(
                    f"Symbol '{order.symbol}' not found on any enabled venue. "
                    f"Known symbols: {sorted(known_symbols)}"
                )
            # Symbol exists but all venue CBs are open — raise, don't fallback silently
            raise RuntimeError(
                f"No venues available for '{order.symbol}' — "
                "all circuit breakers open or no order book data for this symbol"
            )

        scored.sort(key=lambda s: s.total, reverse=True)

        # Proportional allocation: distribute quantity across top venues weighted by score * capacity.
        # Single-venue orders go entirely to the best venue.
        candidates = [s for s in scored[:order.max_splits] if s.available_qty >= order.min_split_qty or not scored[:scored.index(s)]]
        if not candidates:
            candidates = scored[:1]  # guarantee at least one leg

        # Weight = score * min(available_qty, order.quantity) — score quality × capacity
        weights = [s.total * min(s.available_qty, order.quantity) for s in candidates]
        total_w = sum(weights) or 1.0

        legs: List[RoutingLeg] = []
        remaining = order.quantity

        for idx, score in enumerate(candidates):
            if remaining <= 0:
                break

            # First leg takes its proportional share; last leg takes all remaining
            if idx == len(candidates) - 1:
                alloc = remaining
            else:
                alloc = round(order.quantity * weights[idx] / total_w)

            alloc = min(alloc, remaining)
            # Skip legs that are below minimum except the first (which guarantees a route)
            if alloc < order.min_split_qty and legs:
                if remaining < order.min_split_qty:
                    break
                alloc = remaining  # fold remainder into this leg

            if alloc <= 0:
                continue

            venue_cfg = self.venues[score.venue]
            book      = self.cache.get(score.venue, order.symbol)
            price     = order.price
            if price is None and book:
                # Use mid-price for market orders (more realistic than best ask/bid alone)
                if book.best_ask and book.best_bid:
                    mid   = (book.best_ask.price + book.best_bid.price) / 2
                    price = round(mid * (1.0002 if order.side == OrderSide.BUY else 0.9998), 6)
                else:
                    lvl   = book.best_ask if order.side == OrderSide.BUY else book.best_bid
                    price = lvl.price if lvl else None

            legs.append(RoutingLeg(
                venue=score.venue,
                symbol=order.symbol,
                quantity=alloc,
                price=price,
                currency=venue_cfg.currency,
                estimated_cost=alloc * (
                    venue_cfg.taker_fee +
                    self.fx.get_conversion_cost(order.base_currency, venue_cfg.currency)
                ),
            ))
            remaining -= alloc

        elapsed_us = (time.perf_counter_ns() - start_ns) / 1_000

        primary = legs[0].venue if legs else "NONE"
        metrics.observe("sor_routing_latency_us", elapsed_us, venue=primary)
        metrics.inc("sor_orders_routed_total", venue=primary)
        if len(legs) > 1:
            metrics.inc("sor_split_orders_total")

        return RoutingDecision(
            order_id=order.client_order_id,
            symbol=order.symbol,
            total_quantity=order.quantity,
            legs=legs,
            primary_venue=primary,
            routing_latency_us=elapsed_us,
            venue_scores=scored,
        )

    def get_circuit_breaker_stats(self) -> List[dict]:
        return [cb.get_stats() for cb in self.circuit_breakers.values()]
