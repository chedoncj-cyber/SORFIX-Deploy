"""
Smart Order Router — core routing logic.
Scores venues using weighted factors and splits orders to minimize cost + latency.
Weights match the PDF spec: liquidity 30%, spread 20%, fee 20%, FX 20%, latency 10%.
"""
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
    liquidity_weight: float = 0.30
    spread_weight: float    = 0.20
    fee_weight: float       = 0.20
    fx_weight: float        = 0.20
    latency_weight: float   = 0.10
    max_splits: int         = 5
    min_split_qty: float    = 100.0


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
        import math
        venue = self.venues[venue_name]
        cfg   = self.config

        avail     = book.liquidity_at_levels(3)
        liquidity = min(1.0, avail / max(order.quantity, 1))

        raw_spread = book.spread if book.spread is not None else 0.05
        spread     = max(0.0, 1.0 - raw_spread / 0.05)

        fee = max(0.0, 1.0 - venue.taker_fee / 0.005)

        fx_cost_val = self.fx.get_conversion_cost(order.base_currency, venue.currency)
        fx_cost     = max(0.0, 1.0 - fx_cost_val)

        latency = max(0.0, 1.0 - venue.latency_ms / 100.0)

        # Market impact penalty: sqrt model — larger order relative to book depth costs more
        participation = order.quantity / max(avail, 1.0)
        market_impact_penalty = min(0.5, 0.1 * math.sqrt(participation))
        liquidity = max(0.0, liquidity - market_impact_penalty)

        total = (
            liquidity * cfg.liquidity_weight +
            spread    * cfg.spread_weight    +
            fee       * cfg.fee_weight       +
            fx_cost   * cfg.fx_weight        +
            latency   * cfg.latency_weight
        )

        return VenueScore(
            venue=venue_name,
            total=total,
            liquidity=liquidity,
            spread=spread,
            fee=fee,
            fx_cost=fx_cost,
            latency=latency,
            available_qty=avail,
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

        legs: List[RoutingLeg] = []
        remaining = order.quantity

        for score in scored[:order.max_splits]:
            if remaining <= 0:
                break
            # First leg always proceeds regardless of available_qty to guarantee a route;
            # subsequent legs must meet min_split_qty to avoid tiny, inefficient fills.
            if score.available_qty < order.min_split_qty and legs:
                continue

            alloc = min(remaining, score.available_qty) if score.available_qty > 0 else remaining
            if alloc <= 0:
                continue
            if alloc < order.min_split_qty and legs:
                break

            venue_cfg = self.venues[score.venue]
            book      = self.cache.get(score.venue, order.symbol)
            price     = order.price
            if price is None and book:
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
