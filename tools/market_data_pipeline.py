"""
Market data pipeline — simulates Kafka-based ingestion per the PDF architecture.
In production: subscribe to real Kafka topics per venue instead of _tick().
Populates ShardedOrderBookCache with live-updating order book data.
"""
import logging
import math
import threading
import time
import random
from typing import Callable, Dict, List

from tools.order_book_cache import ShardedOrderBookCache, PriceLevel, OrderBook
from tools.monitoring import metrics
from tools.companies_data import get_venue_symbols_for_pipeline

logger = logging.getLogger("market_data_pipeline")


# All listed companies across NYSE, LSE, HKEX, TSE — sourced from companies_data.py
VENUE_SYMBOLS: Dict[str, Dict[str, Dict]] = get_venue_symbols_for_pipeline()


def _generate_book(venue: str, symbol: str, mid: float, depth: int = 10) -> OrderBook:
    """
    Generate a realistic 10-level order book.
    - Tick: 0.5bps of mid (tight institutional spread)
    - Quantities: exponential decay with depth, large base for liquid venues
    - JSE/NGX have deeper books; GSE/NSE slightly shallower
    """
    # Tighter 0.5bps tick — realistic for electronic limit order books
    tick = max(0.0001, round(mid * 0.00005, 8))

    # Venue liquidity multipliers — NYSE/LSE are deepest, HKEX mid, TSE/SSE/SZSE slightly shallower
    liq_mult = {"NYSE": 4.0, "LSE": 3.0, "HKEX": 2.5, "SSE": 2.0,
                "SZSE": 1.8, "TSE": 2.0, "EURONEXT": 2.5,
                "TADAWUL": 1.5, "NSE_IN": 2.0}.get(venue, 1.5)
    base_qty = int(random.randint(8_000, 25_000) * liq_mult)

    bids, asks = [], []
    for i in range(depth):
        # Exponential decay in quantity with depth level
        decay = math.exp(-0.25 * i)
        qty   = max(100, int(base_qty * decay * random.uniform(0.75, 1.25)))
        bids.append(PriceLevel(price=round(mid - tick * (i + 1), 6), quantity=qty, venue=venue))
        asks.append(PriceLevel(price=round(mid + tick * (i + 1), 6), quantity=qty, venue=venue))
    return OrderBook(symbol=symbol, venue=venue, bids=bids, asks=asks,
                     last_update_ns=time.perf_counter_ns())


class MarketDataPipeline:
    """
    Simulates market data ingestion from Kafka topics.
    Each _tick() applies a random walk to mid-prices and refreshes order books.
    Target: 50,000+ updates/sec (PDF §5). Achieved with 0.1s interval + all venues.
    """

    def __init__(self, cache: ShardedOrderBookCache, update_interval: float = 0.1):
        self.cache = cache
        self.update_interval = update_interval
        self._running = False
        self._thread: threading.Thread = None
        self._prices: Dict[str, Dict[str, float]] = {
            venue: {sym: data["price"] for sym, data in syms.items()}
            for venue, syms in VENUE_SYMBOLS.items()
        }
        self._update_count = 0
        self._callbacks: List[Callable] = []
        self._lock = threading.Lock()

    def on_update(self, callback: Callable):
        with self._lock:
            self._callbacks.append(callback)

    def _tick(self):
        """
        Geometric Brownian Motion price walk: dS = S * exp((μ - ½σ²)dt + σ√dt · Z)
        Zero drift (μ=0) for simulation. Each tick is dt = update_interval seconds.
        """
        dt    = self.update_interval
        count = 0
        for venue, symbols in VENUE_SYMBOLS.items():
            for symbol, data in symbols.items():
                sigma = data["vol"]
                # GBM log-normal step
                z          = random.gauss(0.0, 1.0)
                gbm_factor = math.exp((-0.5 * sigma ** 2) * dt + sigma * math.sqrt(dt) * z)
                with self._lock:
                    self._prices[venue][symbol] = max(
                        self._prices[venue][symbol] * gbm_factor, 0.0001
                    )
                    price = self._prices[venue][symbol]
                book = _generate_book(venue, symbol, price)
                self.cache.put(book)
                count += 1
        with self._lock:
            self._update_count += count
            update_count = self._update_count
            callbacks = list(self._callbacks)  # snapshot under lock — safe with on_update()
        metrics.inc("market_data_updates_total", value=count)
        metrics.set_gauge("market_data_cache_books", self.cache.stats()["total_books"])
        for cb in callbacks:
            try:
                cb(update_count)
            except Exception as exc:
                logger.debug("Market data callback raised: %s", exc, exc_info=True)

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
        try:
            self._thread = threading.Thread(
                target=self._run, daemon=True, name="MarketDataPipeline"
            )
            self._thread.start()
        except Exception:
            with self._lock:
                self._running = False
            raise

    def stop(self):
        with self._lock:
            self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self):
        while self._running:
            try:
                self._tick()
            except Exception as exc:
                logger.exception("MarketDataPipeline _tick() error")
            time.sleep(self.update_interval)

    def inject_price(self, venue: str, symbol: str, price: float):
        """Override a price directly — useful for testing SOR routing decisions."""
        with self._lock:
            if venue not in self._prices or symbol not in self._prices[venue]:
                return
            self._prices[venue][symbol] = price
        # Generate and store the book outside the lock — both ops are independently thread-safe.
        book = _generate_book(venue, symbol, price)
        self.cache.put(book)

    def get_valid_symbols(self, venue: str) -> set:
        """Return the static set of symbols for a venue — available before cache is populated."""
        return set(VENUE_SYMBOLS.get(venue, {}).keys())

    def get_stats(self) -> dict:
        with self._lock:
            return {
                "updates_processed": self._update_count,
                "running": self._running,
                "venues": list(VENUE_SYMBOLS.keys()),
                "symbols_per_venue": {v: len(s) for v, s in VENUE_SYMBOLS.items()},
            }
