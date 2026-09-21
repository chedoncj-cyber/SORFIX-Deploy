# tools/position_ledger.py
"""
Internal position ledger — tracks open positions per symbol per venue.
Back-office Phase 1: pure in-process tracking, no external CCP connectivity.
"""
import sqlite3, threading, time, logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger("position_ledger")

@dataclass
class Position:
    symbol: str
    venue: str
    net_qty: float = 0.0       # positive = long, negative = short
    avg_cost: float = 0.0
    realized_pnl: float = 0.0
    last_updated: float = field(default_factory=time.time)

class PositionLedger:
    def __init__(self, db_path: str = None):
        self._lock = threading.Lock()
        self._positions: Dict[str, Position] = {}  # key = "SYMBOL:VENUE"
        self._db_path = db_path or str(Path(__file__).parent.parent / "data" / "positions.db")
        self._init_db()
        self._load_from_db()

    def _init_db(self):
        Path(self._db_path).parent.mkdir(exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    symbol TEXT NOT NULL,
                    venue  TEXT NOT NULL,
                    net_qty REAL DEFAULT 0,
                    avg_cost REAL DEFAULT 0,
                    realized_pnl REAL DEFAULT 0,
                    last_updated REAL,
                    PRIMARY KEY (symbol, venue)
                )
            """)
            conn.commit()

    def _load_from_db(self):
        with sqlite3.connect(self._db_path) as conn:
            for row in conn.execute("SELECT symbol,venue,net_qty,avg_cost,realized_pnl,last_updated FROM positions"):
                key = f"{row[0]}:{row[1]}"
                self._positions[key] = Position(row[0],row[1],row[2],row[3],row[4],row[5])

    def _persist(self, pos: Position):
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                INSERT INTO positions(symbol,venue,net_qty,avg_cost,realized_pnl,last_updated)
                VALUES(?,?,?,?,?,?)
                ON CONFLICT(symbol,venue) DO UPDATE SET
                    net_qty=excluded.net_qty, avg_cost=excluded.avg_cost,
                    realized_pnl=excluded.realized_pnl, last_updated=excluded.last_updated
            """, (pos.symbol, pos.venue, pos.net_qty, pos.avg_cost, pos.realized_pnl, pos.last_updated))
            conn.commit()

    def update(self, symbol: str, venue: str, qty: float, price: float, side: str):
        """Apply a fill to the ledger. side='buy' or 'sell'."""
        key = f"{symbol}:{venue}"
        signed_qty = qty if side.lower() == "buy" else -qty
        with self._lock:
            pos = self._positions.get(key) or Position(symbol, venue)
            old_qty = pos.net_qty
            if pos.net_qty == 0:
                pos.avg_cost = price
            elif (old_qty > 0 and signed_qty > 0) or (old_qty < 0 and signed_qty < 0):
                total_cost = abs(pos.net_qty) * pos.avg_cost + abs(signed_qty) * price
                pos.avg_cost = total_cost / (abs(pos.net_qty) + abs(signed_qty))
            else:
                closing = min(abs(signed_qty), abs(pos.net_qty))
                if side.lower() == "sell":
                    pos.realized_pnl += closing * (price - pos.avg_cost)
                else:
                    pos.realized_pnl += closing * (pos.avg_cost - price)
            pos.net_qty += signed_qty
            pos.last_updated = time.time()
            self._positions[key] = pos
            self._persist(pos)
            logger.debug("Position %s: net_qty=%.2f avg_cost=%.4f realized_pnl=%.2f", key, pos.net_qty, pos.avg_cost, pos.realized_pnl)

    def get(self, symbol: str, venue: str) -> Optional[Position]:
        with self._lock:
            return self._positions.get(f"{symbol}:{venue}")

    def all_positions(self) -> List[dict]:
        with self._lock:
            return [
                {"symbol": p.symbol, "venue": p.venue, "net_qty": p.net_qty,
                 "avg_cost": p.avg_cost, "realized_pnl": round(p.realized_pnl, 4),
                 "last_updated": p.last_updated}
                for p in self._positions.values() if p.net_qty != 0
            ]

    def summary(self) -> dict:
        with self._lock:
            total_pnl = sum(p.realized_pnl for p in self._positions.values())
            return {"open_positions": sum(1 for p in self._positions.values() if p.net_qty != 0),
                    "total_realized_pnl": round(total_pnl, 4),
                    "symbols_traded": len(self._positions)}
