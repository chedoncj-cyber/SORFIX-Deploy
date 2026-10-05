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
from typing import Callable, Dict, List, Optional

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

    async def run_async(self):
        """Run as an asyncio task — cooperative sleep releases event loop between ticks."""
        import asyncio
        with self._lock:
            if self._running:
                return
            self._running = True
        loop = asyncio.get_running_loop()
        try:
            while self._running:
                try:
                    await loop.run_in_executor(None, self._tick)
                except Exception:
                    logger.exception("MarketDataPipeline _tick() error")
                await asyncio.sleep(self.update_interval)
        finally:
            with self._lock:
                self._running = False

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


# ── Bond yield simulation ──────────────────────────────────────────────────────
# Mid yield in %, vol in bps/day  (GBM on yield, not price)

SIMULATED_BONDS: dict = {
    # ISIN: {country, coupon_pct, maturity_yr, mid_yield_pct, vol_bps}
    "US912810TM85": {"country": "USA",    "coupon": 4.50, "mat": 10, "yield": 4.45, "vol": 2.0},
    "US912810TM86": {"country": "USA",    "coupon": 3.75, "mat": 30, "yield": 4.62, "vol": 2.5},
    "GB00BN65WP19": {"country": "UK",     "coupon": 3.25, "mat": 10, "yield": 4.15, "vol": 2.2},
    "DE0001102580": {"country": "GER",    "coupon": 2.50, "mat": 10, "yield": 2.68, "vol": 1.8},
    "GH0000000XXX": {"country": "GHANA",  "coupon": 15.5, "mat": 5,  "yield": 15.3, "vol": 8.0},
    "NG0000000XXX": {"country": "NIGERIA","coupon": 17.8, "mat": 7,  "yield": 17.6, "vol": 10.0},
    "ZA0006970756": {"country": "SA",     "coupon": 8.00, "mat": 10, "yield": 8.25, "vol": 4.0},
    "KE2000007778": {"country": "KENYA",  "coupon": 13.5, "mat": 5,  "yield": 13.2, "vol": 6.0},
}

# ── FX rate simulation ─────────────────────────────────────────────────────────
# Spot rate vs USD, annualised vol

SIMULATED_FX_RATES: dict = {
    "EURUSD": {"rate": 1.0875, "vol": 0.06},
    "GBPUSD": {"rate": 1.2720, "vol": 0.07},
    "USDJPY": {"rate": 149.50, "vol": 0.08},
    "USDCHF": {"rate": 0.8950, "vol": 0.05},
    "AUDUSD": {"rate": 0.6580, "vol": 0.09},
    "USDCAD": {"rate": 1.3620, "vol": 0.06},
    "NZDUSD": {"rate": 0.6030, "vol": 0.10},
    "USDZAR": {"rate": 18.55,  "vol": 0.14},
    "USDGHS": {"rate": 14.20,  "vol": 0.18},
    "USDNGN": {"rate": 1580.0, "vol": 0.22},
    "USDKES": {"rate": 131.50, "vol": 0.12},
    "USDBRL": {"rate": 4.97,   "vol": 0.16},
    "USDINR": {"rate": 83.40,  "vol": 0.07},
    "USDMXN": {"rate": 17.15,  "vol": 0.12},
}


class BondMarketData:
    """
    Simulates bond yield/price updates via GBM on yield.
    In production: subscribe to a Bloomberg or Refinitiv bond data feed.
    """

    def __init__(self, update_interval: float = 5.0):
        self._yields: dict = {isin: d["yield"] for isin, d in SIMULATED_BONDS.items()}
        self._lock = threading.Lock()
        self._interval = update_interval
        self._running = False
        self._thread: threading.Thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="BondMD")
        self._thread.start()

    def stop(self):
        self._running = False

    async def run_async(self):
        """Run as an asyncio task — cooperative sleep releases event loop between ticks."""
        import asyncio
        self._running = True
        loop = asyncio.get_running_loop()
        try:
            while self._running:
                try:
                    await loop.run_in_executor(None, self._tick)
                except Exception:
                    logger.exception("BondMarketData _tick() error")
                await asyncio.sleep(self._interval)
        finally:
            self._running = False

    def get_yield(self, isin: str) -> Optional[float]:
        with self._lock:
            return self._yields.get(isin.upper())

    def get_rate_snapshot(self) -> dict:
        with self._lock:
            return dict(self._yields)

    def _run(self):
        while self._running:
            self._tick()
            time.sleep(self._interval)

    def _tick(self):
        dt = self._interval / 86_400  # fraction of trading day
        with self._lock:
            for isin, data in SIMULATED_BONDS.items():
                vol_bps = data["vol"] * 0.0001  # bps → decimal
                z = random.gauss(0.0, 1.0)
                # Random walk on yield (arithmetic, not GBM — yields can go near zero)
                self._yields[isin] = max(
                    0.01,
                    self._yields[isin] + vol_bps * math.sqrt(dt) * z * 100
                )


class FXMarketData:
    """
    Simulates FX spot rate updates via GBM.
    In production: subscribe to an ECN (EBS, Reuters Matching, or LMAX feed).
    """

    def __init__(self, update_interval: float = 0.5):
        self._rates: dict = {pair: d["rate"] for pair, d in SIMULATED_FX_RATES.items()}
        self._lock = threading.Lock()
        self._interval = update_interval
        self._running = False
        self._thread: threading.Thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="FXMD")
        self._thread.start()

    def stop(self):
        self._running = False

    async def run_async(self):
        """Run as an asyncio task — cooperative sleep releases event loop between ticks."""
        import asyncio
        self._running = True
        loop = asyncio.get_running_loop()
        try:
            while self._running:
                try:
                    await loop.run_in_executor(None, self._tick)
                except Exception:
                    logger.exception("FXMarketData _tick() error")
                await asyncio.sleep(self._interval)
        finally:
            self._running = False

    def get_rate(self, pair: str) -> Optional[float]:
        pair = pair.replace("/", "").upper()
        with self._lock:
            return self._rates.get(pair)

    def get_rate_snapshot(self) -> dict:
        with self._lock:
            return dict(self._rates)

    def _run(self):
        while self._running:
            self._tick()
            time.sleep(self._interval)

    def _tick(self):
        dt = self._interval / (252 * 6.5 * 3600)  # fraction of trading year
        with self._lock:
            for pair, data in SIMULATED_FX_RATES.items():
                vol = data["vol"]
                z = random.gauss(0.0, 1.0)
                gbm = math.exp(-0.5 * vol**2 * dt + vol * math.sqrt(dt) * z)
                self._rates[pair] = max(0.0001, self._rates[pair] * gbm)
