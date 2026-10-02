"""Dark Pool crossing engine — matches orders internally before routing to lit venues."""
import threading, time, uuid
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DarkOrder:
    id: str; symbol: str; side: str; quantity: float
    price: Optional[float]; firm_name: str; added_at: float
    ttl_seconds: int = 300; remaining: float = 0.0

    def __post_init__(self):
        if self.remaining == 0.0: self.remaining = self.quantity

    @property
    def is_expired(self): return time.time() - self.added_at > self.ttl_seconds

    def to_dict(self):
        return {"id": self.id, "symbol": self.symbol, "side": self.side,
                "quantity": self.quantity, "remaining": self.remaining,
                "price": self.price, "firm_name": self.firm_name,
                "added_at": self.added_at,
                "age_seconds": round(time.time() - self.added_at, 1)}


@dataclass
class CrossResult:
    crossed: bool; cross_qty: float; cross_price: float
    lit_qty: float; counterparty: Optional[str]; cross_id: Optional[str]


class DarkPoolEngine:
    def __init__(self):
        self._pool: dict = {}; self._crosses: list = []; self._lock = threading.Lock()

    def add(self, symbol, side, quantity, price, firm_name="SORFIX", ttl_seconds=300):
        with self._lock:
            self._prune()
            o = DarkOrder(id=str(uuid.uuid4())[:8].upper(), symbol=symbol.upper(),
                          side=side.lower(), quantity=quantity, price=price,
                          firm_name=firm_name, added_at=time.time(), ttl_seconds=ttl_seconds)
            self._pool[o.id] = o; return o

    def try_cross(self, symbol, side, quantity, midpoint=None):
        with self._lock:
            self._prune()
            symbol = symbol.upper(); side = side.lower()
            opposite = "sell" if side == "buy" else "buy"
            candidates = sorted(
                [o for o in self._pool.values() if o.symbol == symbol and o.side == opposite and o.remaining > 0],
                key=lambda o: o.added_at)
            remaining = quantity; crossed = 0.0; counterparty = None
            cross_id = str(uuid.uuid4())[:8].upper() if candidates else None
            for c in candidates:
                if remaining <= 0: break
                fill = min(remaining, c.remaining)
                c.remaining -= fill; remaining -= fill; crossed += fill
                counterparty = c.firm_name
                if c.remaining <= 0: del self._pool[c.id]
            if crossed > 0:
                self._crosses.append({"cross_id": cross_id, "symbol": symbol, "side": side,
                                       "cross_qty": crossed, "cross_price": midpoint or 0.0,
                                       "counterparty": counterparty, "timestamp": time.time()})
            return CrossResult(crossed=(crossed > 0), cross_qty=crossed,
                               cross_price=midpoint or 0.0, lit_qty=remaining,
                               counterparty=counterparty, cross_id=cross_id if crossed > 0 else None)

    def snapshot(self, symbol=None):
        with self._lock:
            self._prune()
            return [o.to_dict() for o in self._pool.values()
                    if symbol is None or o.symbol == symbol.upper()]

    def crossing_log(self, limit=100):
        with self._lock: return list(reversed(self._crosses[-limit:]))

    def stats(self):
        with self._lock:
            self._prune()
            return {"pool_size": len(self._pool), "total_crosses": len(self._crosses),
                    "total_cross_qty": sum(c["cross_qty"] for c in self._crosses)}

    def _prune(self):
        dead = [k for k, o in self._pool.items() if o.is_expired]
        for k in dead: del self._pool[k]
