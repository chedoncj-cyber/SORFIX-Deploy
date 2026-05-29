"""
Sharded in-memory order book cache.
256 shards to minimize lock contention on the hot path.
"""
import threading
from dataclasses import dataclass, field
from typing import Optional, Dict, List

SHARD_COUNT = 256


@dataclass
class PriceLevel:
    price: float
    quantity: float
    venue: str


@dataclass
class OrderBook:
    symbol: str
    venue: str
    bids: List[PriceLevel] = field(default_factory=list)  # sorted descending
    asks: List[PriceLevel] = field(default_factory=list)  # sorted ascending
    last_update_ns: int = 0

    @property
    def best_bid(self) -> Optional[PriceLevel]:
        return self.bids[0] if self.bids else None

    @property
    def best_ask(self) -> Optional[PriceLevel]:
        return self.asks[0] if self.asks else None

    @property
    def spread(self) -> Optional[float]:
        if self.best_bid and self.best_ask:
            mid = (self.best_bid.price + self.best_ask.price) / 2
            return (self.best_ask.price - self.best_bid.price) / mid if mid > 1e-9 else None
        return None

    def liquidity_at_levels(self, n: int = 3) -> float:
        bid_liq = sum(lvl.quantity for lvl in self.bids[:n])
        ask_liq = sum(lvl.quantity for lvl in self.asks[:n])
        return (bid_liq + ask_liq) / 2


class _Shard:
    def __init__(self):
        self.books: Dict[str, OrderBook] = {}
        self.lock = threading.RLock()


class ShardedOrderBookCache:
    def __init__(self, shard_count: int = SHARD_COUNT):
        if shard_count < 1 or (shard_count & (shard_count - 1)) != 0:
            raise ValueError(f"shard_count must be a power of 2, got {shard_count}")
        self._shards = [_Shard() for _ in range(shard_count)]
        self._mask = shard_count - 1

    def _shard(self, key: str) -> _Shard:
        return self._shards[hash(key) & self._mask]

    def get(self, venue: str, symbol: str) -> Optional[OrderBook]:
        key = f"{venue}:{symbol}"
        shard = self._shard(key)
        with shard.lock:
            return shard.books.get(key)

    def put(self, book: OrderBook):
        key = f"{book.venue}:{book.symbol}"
        shard = self._shard(key)
        with shard.lock:
            shard.books[key] = book

    def get_all_venues_for_symbol(self, symbol: str) -> List[OrderBook]:
        results = []
        for shard in self._shards:
            with shard.lock:
                for key, book in shard.books.items():
                    if key.endswith(f":{symbol}"):
                        results.append(book)
        return results

    def get_known_symbols(self) -> set:
        """Return the set of all symbols currently held across all shards."""
        symbols: set = set()
        for shard in self._shards:
            with shard.lock:
                for key in shard.books:
                    symbols.add(key.split(":", 1)[1])
        return symbols

    def stats(self) -> dict:
        total = 0
        for shard in self._shards:
            with shard.lock:
                total += len(shard.books)
        return {"total_books": total, "shard_count": len(self._shards)}
