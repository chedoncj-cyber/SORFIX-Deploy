"""
Position tracker — net qty, average cost, realized P&L per symbol.
Thread-safe; updated by the execution engine after each fill.
"""
import logging
import threading
from dataclasses import dataclass, field
from typing import Dict, Optional

logger = logging.getLogger("position_tracker")


@dataclass
class Position:
    symbol: str
    net_qty: float = 0.0
    avg_cost: float = 0.0
    realized_pnl: float = 0.0
    total_buys: int = 0
    total_sells: int = 0
    total_volume: float = 0.0

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "net_qty": round(self.net_qty, 6),
            "avg_cost": round(self.avg_cost, 6),
            "realized_pnl": round(self.realized_pnl, 6),
            "total_buys": self.total_buys,
            "total_sells": self.total_sells,
            "total_volume": round(self.total_volume, 6),
        }


class PositionTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self._positions: Dict[str, Position] = {}
        self._fill_count: int = 0

    def record_fill(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: float,
    ):
        """Update position after a fill. side must be 'buy' or 'sell'."""
        if qty <= 0 or price <= 0:
            return
        symbol = symbol.upper()
        with self._lock:
            pos = self._positions.setdefault(symbol, Position(symbol=symbol))
            self._fill_count += 1

            if side.lower() == "buy":
                pos.total_buys += 1
                pos.total_volume += qty
                new_net = pos.net_qty + qty
                if pos.net_qty < 0:
                    # Covering a short position.
                    cover_qty = min(qty, abs(pos.net_qty))
                    # Realize P&L on covered portion: profit when buy-back < short entry price.
                    pos.realized_pnl += cover_qty * (pos.avg_cost - price)
                    if new_net <= 0:
                        # Still short (or exactly flat) — avg_cost unchanged.
                        pos.net_qty = new_net
                        if new_net == 0:
                            pos.avg_cost = 0.0
                    else:
                        # Flipped from short to long — new avg_cost is purely the fill price.
                        pos.net_qty = new_net
                        pos.avg_cost = price
                else:
                    # Adding to existing long or opening from flat.
                    total_value = pos.avg_cost * pos.net_qty + price * qty
                    pos.net_qty = new_net
                    pos.avg_cost = total_value / pos.net_qty if pos.net_qty > 0 else price
            else:
                pos.total_sells += 1
                pos.total_volume += qty
                new_net = pos.net_qty - qty
                if pos.net_qty > 0:
                    # Closing (some of) a long position.
                    close_qty = min(qty, pos.net_qty)
                    pos.realized_pnl += close_qty * (price - pos.avg_cost)
                    if new_net >= 0:
                        # Still long (or flat) — avg_cost unchanged.
                        pos.net_qty = new_net
                        if new_net == 0:
                            pos.avg_cost = 0.0
                    else:
                        # Flipped from long to short — avg_cost is the short entry price.
                        pos.net_qty = new_net
                        pos.avg_cost = price
                else:
                    # Adding to existing short or opening from flat.
                    pos.net_qty = new_net
                    pos.avg_cost = price

            logger.debug(
                "Position %s after %s %.0f @ %.4f: net=%.0f avg=%.4f rpnl=%.2f",
                symbol, side, qty, price, pos.net_qty, pos.avg_cost, pos.realized_pnl,
            )

    def get_position(self, symbol: str) -> Optional[Position]:
        with self._lock:
            return self._positions.get(symbol.upper())

    def get_all(self) -> list:
        with self._lock:
            return [p.to_dict() for p in self._positions.values()]

    def get_stats(self) -> dict:
        with self._lock:
            total_rpnl = sum(p.realized_pnl for p in self._positions.values())
            return {
                "symbols_tracked": len(self._positions),
                "total_fills": self._fill_count,
                "total_realized_pnl": round(total_rpnl, 6),
            }
