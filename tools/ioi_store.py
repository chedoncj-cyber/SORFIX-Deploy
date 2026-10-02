"""IOI (Indication of Interest) store — in-memory board of buy/sell interest."""
import threading, time, uuid
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class IOI:
    id: str; symbol: str; side: str; quantity: float
    price: Optional[float]; firm_name: str; contact: str; notes: str
    ttl_seconds: int; created_at: float; status: str = "active"
    matched_with: Optional[str] = None

    @property
    def is_expired(self): return time.time() - self.created_at > self.ttl_seconds

    def to_dict(self):
        return {"id": self.id, "symbol": self.symbol, "side": self.side,
                "quantity": self.quantity, "price": self.price,
                "firm_name": self.firm_name, "contact": self.contact,
                "notes": self.notes, "ttl_seconds": self.ttl_seconds,
                "created_at": self.created_at,
                "expires_at": self.created_at + self.ttl_seconds,
                "status": "expired" if (self.status == "active" and self.is_expired) else self.status,
                "matched_with": self.matched_with,
                "age_seconds": round(time.time() - self.created_at, 1)}


class IOIStore:
    def __init__(self, max_iois: int = 1000):
        self._iois: dict = {}; self._lock = threading.Lock(); self._max = max_iois

    def post(self, symbol, side, quantity, price, firm_name, contact="", notes="", ttl_seconds=3600):
        with self._lock:
            self._evict_expired()
            ioi = IOI(id=str(uuid.uuid4())[:8].upper(), symbol=symbol.upper(),
                      side=side.lower(), quantity=quantity, price=price,
                      firm_name=firm_name, contact=contact, notes=notes,
                      ttl_seconds=ttl_seconds, created_at=time.time())
            self._iois[ioi.id] = ioi
            return ioi

    def list(self, symbol=None, side=None, include_expired=False):
        with self._lock:
            res = []
            for ioi in self._iois.values():
                if ioi.status in ("matched", "cancelled"): continue
                if ioi.is_expired and not include_expired: continue
                if symbol and ioi.symbol != symbol.upper(): continue
                if side and ioi.side != side.lower(): continue
                res.append(ioi.to_dict())
            return sorted(res, key=lambda x: x["created_at"], reverse=True)

    def cancel(self, ioi_id, firm_name):
        with self._lock:
            ioi = self._iois.get(ioi_id.upper())
            if not ioi or ioi.firm_name != firm_name: return None
            ioi.status = "cancelled"; return ioi.to_dict()

    def match(self, id1, id2):
        with self._lock:
            i1 = self._iois.get(id1.upper()); i2 = self._iois.get(id2.upper())
            if not i1 or not i2 or i1.side == i2.side: return None
            i1.status = i2.status = "matched"
            i1.matched_with = i2.id; i2.matched_with = i1.id
            return {"matched": True, "ioi_1": i1.to_dict(), "ioi_2": i2.to_dict(),
                    "symbol": i1.symbol, "matched_qty": min(i1.quantity, i2.quantity)}

    def get(self, ioi_id):
        with self._lock:
            ioi = self._iois.get(ioi_id.upper()); return ioi.to_dict() if ioi else None

    def stats(self):
        with self._lock:
            return {"active": sum(1 for i in self._iois.values() if i.status == "active" and not i.is_expired),
                    "expired": sum(1 for i in self._iois.values() if i.is_expired),
                    "matched": sum(1 for i in self._iois.values() if i.status == "matched"),
                    "total": len(self._iois)}

    def _evict_expired(self):
        dead = [k for k, v in self._iois.items() if v.is_expired or v.status in ("expired","cancelled")]
        for k in dead: del self._iois[k]
