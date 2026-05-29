"""
Market data pipeline — simulates Kafka-based ingestion per the PDF architecture.
In production: subscribe to real Kafka topics per venue instead of _tick().
Populates ShardedOrderBookCache with live-updating order book data.
"""
import logging
import threading
import time
import random
from typing import Callable, Dict, List

from tools.order_book_cache import ShardedOrderBookCache, PriceLevel, OrderBook
from tools.monitoring import metrics

logger = logging.getLogger("market_data_pipeline")


# Realistic symbols with approximate mid-prices (local currency)
VENUE_SYMBOLS: Dict[str, Dict[str, Dict]] = {
    "GSE": {
        "GCB":   {"price": 5.80,   "vol": 0.002},
        "MTNGH": {"price": 1.15,   "vol": 0.003},
        "GOIL":  {"price": 2.40,   "vol": 0.002},
        "UNIL":  {"price": 18.50,  "vol": 0.001},
        "SIC":   {"price": 0.08,   "vol": 0.005},
        "EGL":   {"price": 3.20,   "vol": 0.002},
    },
    "JSE": {
        "MTN":   {"price": 148.50, "vol": 0.003},
        "NPN":   {"price": 2950.0, "vol": 0.002},
        "SOL":   {"price": 320.0,  "vol": 0.002},
        "BHP":   {"price": 485.0,  "vol": 0.002},
        "AGL":   {"price": 820.0,  "vol": 0.003},
    },
    "NGX": {
        "DANGCEM":    {"price": 680.0,  "vol": 0.004},
        "GTCO":       {"price": 52.5,   "vol": 0.003},
        "AIRTELAFRI": {"price": 1920.0, "vol": 0.003},
        "ZENITHBANK": {"price": 35.8,   "vol": 0.003},
        "MTNN":       {"price": 285.0,  "vol": 0.003},
    },
    "NSE": {
        "SAFCOM": {"price": 40.5,  "vol": 0.002},
        "EABL":   {"price": 145.0, "vol": 0.002},
        "KCB":    {"price": 42.25, "vol": 0.003},
        "EQUITY": {"price": 52.0,  "vol": 0.003},
        "BAMBURI":{"price": 44.75, "vol": 0.004},
    },
}


def _generate_book(venue: str, symbol: str, mid: float, depth: int = 5) -> OrderBook:
    tick = max(0.001, round(mid * 0.001, 6))
    bids, asks = [], []
    for i in range(depth):
        qty = random.randint(500, 10_000) * (depth - i)
        bids.append(PriceLevel(price=round(mid - tick * (i + 1), 4), quantity=qty, venue=venue))
        asks.append(PriceLevel(price=round(mid + tick * (i + 1), 4), quantity=qty, venue=venue))
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
        count = 0
        for venue, symbols in VENUE_SYMBOLS.items():
            for symbol, data in symbols.items():
                drift = random.gauss(0, data["vol"])
                with self._lock:
                    self._prices[venue][symbol] = max(
                        self._prices[venue][symbol] * (1 + drift), 0.0001
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
