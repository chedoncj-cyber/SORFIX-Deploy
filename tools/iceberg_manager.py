"""Iceberg order manager — show only display_qty; refill slices until total_qty filled."""
import threading, time, uuid
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class IcebergOrder:
    id: str; symbol: str; side: str; total_qty: float; display_qty: float
    price: Optional[float]; base_currency: str; firm_name: str
    created_at: float; filled_qty: float = 0.0; vwap_num: float = 0.0
    status: str = "active"; slices: list = field(default_factory=list)

    @property
    def remaining_qty(self): return max(0.0, self.total_qty - self.filled_qty)
    @property
    def next_slice_qty(self): return min(self.display_qty, self.remaining_qty)
    @property
    def vwap(self): return self.vwap_num / self.filled_qty if self.filled_qty > 0 else None
    @property
    def fill_ratio(self): return self.filled_qty / self.total_qty if self.total_qty > 0 else 0.0

    def to_dict(self):
        return {"id": self.id, "symbol": self.symbol, "side": self.side,
                "total_qty": self.total_qty, "display_qty": self.display_qty,
                "filled_qty": self.filled_qty, "remaining_qty": self.remaining_qty,
                "next_slice_qty": self.next_slice_qty,
                "price": self.price, "base_currency": self.base_currency,
                "vwap": round(self.vwap, 6) if self.vwap else None,
                "fill_ratio": round(self.fill_ratio, 4),
                "status": "completed" if self.remaining_qty <= 0 else self.status,
                "slices": self.slices, "created_at": self.created_at,
                "slice_count": len(self.slices)}


class IcebergManager:
    def __init__(self):
        self._orders: dict = {}; self._lock = threading.Lock()

    def create(self, symbol, side, total_qty, display_qty, price,
               base_currency="USD", firm_name="SORFIX"):
        with self._lock:
            o = IcebergOrder(id=str(uuid.uuid4())[:8].upper(), symbol=symbol.upper(),
                             side=side.lower(), total_qty=total_qty, display_qty=display_qty,
                             price=price, base_currency=base_currency, firm_name=firm_name,
                             created_at=time.time())
            self._orders[o.id] = o; return o

    def record_fill(self, order_id, filled_qty, avg_price):
        with self._lock:
            o = self._orders.get(order_id.upper())
            if not o or o.status != "active": return None
            o.filled_qty += filled_qty; o.vwap_num += filled_qty * avg_price
            o.slices.append({"slice_qty": filled_qty, "avg_price": avg_price,
                              "timestamp": time.time(), "remaining": o.remaining_qty})
            if o.remaining_qty <= 0: o.status = "completed"
            return o

    def cancel(self, order_id):
        with self._lock:
            o = self._orders.get(order_id.upper())
            if not o: return None
            o.status = "cancelled"; return o.to_dict()

    def get(self, order_id):
        with self._lock:
            o = self._orders.get(order_id.upper()); return o.to_dict() if o else None

    def list(self, status=None):
        with self._lock:
            res = [o.to_dict() for o in self._orders.values()]
            if status: res = [o for o in res if o["status"] == status]
            return sorted(res, key=lambda x: x["created_at"], reverse=True)
