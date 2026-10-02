"""Block trade workflow — large order negotiation: submit → match → agree → execute."""
import threading, time, uuid
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BlockResponse:
    id: str; block_id: str; firm_name: str; quantity: float
    counter_price: float; notes: str; submitted_at: float; status: str = "pending"

    def to_dict(self):
        return {"id": self.id, "block_id": self.block_id, "firm_name": self.firm_name,
                "quantity": self.quantity, "counter_price": self.counter_price,
                "notes": self.notes, "submitted_at": self.submitted_at, "status": self.status}


@dataclass
class BlockTrade:
    id: str; symbol: str; side: str; quantity: float; limit_price: Optional[float]
    firm_name: str; contact: str; created_at: float; ttl_seconds: int = 3600
    status: str = "open"; responses: List[BlockResponse] = field(default_factory=list)
    matched_with: Optional[str] = None; agreed_price: Optional[float] = None
    executed_qty: Optional[float] = None; order_id: Optional[str] = None

    @property
    def is_expired(self): return time.time() - self.created_at > self.ttl_seconds

    def to_dict(self):
        return {"id": self.id, "symbol": self.symbol, "side": self.side,
                "quantity": self.quantity, "limit_price": self.limit_price,
                "firm_name": self.firm_name, "contact": self.contact,
                "created_at": self.created_at,
                "status": "expired" if (self.status == "open" and self.is_expired) else self.status,
                "responses": [r.to_dict() for r in self.responses],
                "response_count": len(self.responses),
                "matched_with": self.matched_with, "agreed_price": self.agreed_price,
                "executed_qty": self.executed_qty, "order_id": self.order_id,
                "age_seconds": round(time.time() - self.created_at, 1)}


class BlockTradeEngine:
    MIN_QTY = 5000

    def __init__(self, min_qty=5000):
        self.MIN_QTY = min_qty; self._trades: dict = {}; self._lock = threading.Lock()

    def submit(self, symbol, side, quantity, limit_price, firm_name, contact="", ttl_seconds=3600):
        with self._lock:
            bt = BlockTrade(id=str(uuid.uuid4())[:8].upper(), symbol=symbol.upper(),
                            side=side.lower(), quantity=quantity, limit_price=limit_price,
                            firm_name=firm_name, contact=contact, created_at=time.time(),
                            ttl_seconds=ttl_seconds)
            self._trades[bt.id] = bt; return bt

    def respond(self, block_id, firm_name, quantity, counter_price, notes=""):
        with self._lock:
            bt = self._trades.get(block_id.upper())
            if not bt or bt.status != "open": return None
            r = BlockResponse(id=str(uuid.uuid4())[:8].upper(), block_id=block_id.upper(),
                              firm_name=firm_name, quantity=quantity,
                              counter_price=counter_price, notes=notes, submitted_at=time.time())
            bt.responses.append(r); return r

    def accept(self, block_id, response_id, agreed_price=None):
        with self._lock:
            bt = self._trades.get(block_id.upper())
            if not bt or bt.status != "open": return None
            match = next((r for r in bt.responses if r.id == response_id.upper()), None)
            if not match: return None
            match.status = "accepted"; bt.status = "matched"
            bt.matched_with = match.id; bt.agreed_price = agreed_price or match.counter_price
            for r in bt.responses:
                if r.id != match.id: r.status = "rejected"
            return bt.to_dict()

    def record_execution(self, block_id, order_id, executed_qty):
        with self._lock:
            bt = self._trades.get(block_id.upper())
            if bt: bt.status = "executed"; bt.order_id = order_id; bt.executed_qty = executed_qty

    def cancel(self, block_id, firm_name):
        with self._lock:
            bt = self._trades.get(block_id.upper())
            if not bt or bt.firm_name != firm_name or bt.status in ("executed","cancelled"): return None
            bt.status = "cancelled"; return bt.to_dict()

    def list(self, symbol=None, status=None):
        with self._lock:
            res = [bt.to_dict() for bt in self._trades.values()]
            if symbol: res = [b for b in res if b["symbol"] == symbol.upper()]
            if status: res = [b for b in res if b["status"] == status]
            return sorted(res, key=lambda x: x["created_at"], reverse=True)

    def get(self, block_id):
        with self._lock:
            bt = self._trades.get(block_id.upper()); return bt.to_dict() if bt else None
