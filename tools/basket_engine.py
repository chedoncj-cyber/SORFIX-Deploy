"""Basket/portfolio trading engine — execute multiple stocks as one instruction."""
import threading, time, uuid
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BasketLeg:
    symbol: str; side: str; quantity: float; price: Optional[float]
    status: str = "pending"; filled_qty: float = 0.0
    vwap: Optional[float] = None; order_id: Optional[str] = None; error: Optional[str] = None

    def to_dict(self):
        return {"symbol": self.symbol, "side": self.side, "quantity": self.quantity,
                "price": self.price, "status": self.status, "filled_qty": self.filled_qty,
                "fill_ratio": round(self.filled_qty / self.quantity, 4) if self.quantity > 0 else 0.0,
                "vwap": self.vwap, "order_id": self.order_id, "error": self.error}


@dataclass
class Basket:
    id: str; name: str; legs: List[BasketLeg]; base_currency: str
    firm_name: str; created_at: float; status: str = "pending"
    completed_at: Optional[float] = None; error: Optional[str] = None

    def to_dict(self):
        filled = sum(1 for l in self.legs if l.status == "filled")
        failed = sum(1 for l in self.legs if l.status == "failed")
        return {"id": self.id, "name": self.name, "status": self.status,
                "total_legs": len(self.legs), "filled_legs": filled, "failed_legs": failed,
                "base_currency": self.base_currency, "firm_name": self.firm_name,
                "created_at": self.created_at, "completed_at": self.completed_at,
                "legs": [l.to_dict() for l in self.legs], "error": self.error}


class BasketEngine:
    def __init__(self):
        self._baskets: dict = {}; self._lock = threading.Lock()

    def create(self, name, legs, base_currency="USD", firm_name="SORFIX"):
        with self._lock:
            b = Basket(id=str(uuid.uuid4())[:8].upper(), name=name,
                       legs=[BasketLeg(symbol=l["symbol"].upper(), side=l["side"].lower(),
                                       quantity=float(l["quantity"]),
                                       price=float(l["price"]) if l.get("price") else None)
                             for l in legs],
                       base_currency=base_currency, firm_name=firm_name, created_at=time.time())
            self._baskets[b.id] = b; return b

    def record_leg(self, basket_id, symbol, order_id, filled_qty, vwap, success, error=""):
        with self._lock:
            b = self._baskets.get(basket_id.upper())
            if not b: return None
            for leg in b.legs:
                if leg.symbol == symbol.upper() and leg.status == "pending":
                    leg.order_id = order_id; leg.filled_qty = filled_qty; leg.vwap = vwap
                    leg.status = "filled" if success else "failed"
                    leg.error = error if not success else None; break
            pending = sum(1 for l in b.legs if l.status == "pending")
            if pending == 0:
                filled = sum(1 for l in b.legs if l.status == "filled")
                failed = sum(1 for l in b.legs if l.status == "failed")
                b.status = "completed" if failed == 0 else ("failed" if filled == 0 else "partial")
                b.completed_at = time.time()
            return b

    def get(self, basket_id):
        with self._lock:
            b = self._baskets.get(basket_id.upper()); return b.to_dict() if b else None

    def list(self):
        with self._lock:
            return sorted([b.to_dict() for b in self._baskets.values()],
                          key=lambda x: x["created_at"], reverse=True)

    def cancel(self, basket_id):
        with self._lock:
            b = self._baskets.get(basket_id.upper())
            if b and b.status == "pending":
                b.status = "cancelled"; b.completed_at = time.time()
                for l in b.legs:
                    if l.status == "pending": l.status = "cancelled"
                return b.to_dict()
            return None
