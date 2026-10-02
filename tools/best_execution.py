"""Best Execution reporting — per-order audit trail (MiFID II compatible)."""
import threading, time
from typing import List, Optional


class BestExecutionStore:
    def __init__(self, max_reports: int = 2000):
        self._reports: list = []; self._index: dict = {}
        self._lock = threading.Lock(); self._max = max_reports

    def record(self, order_id, symbol, side, quantity, limit_price,
               routing_decision, execution_result, arrival_price=None):
        venue_scores = routing_decision.get("venue_scores", [])
        legs         = routing_decision.get("legs", [])
        total_filled = execution_result.get("total_filled", 0.0)
        vwap         = execution_result.get("vwap")
        sorted_v     = sorted(venue_scores, key=lambda v: v.get("score", 0), reverse=True)
        chosen       = {l["venue"] for l in legs}

        slippage_bps = None
        if vwap and arrival_price and arrival_price > 0:
            diff = (vwap - arrival_price) if side == "buy" else (arrival_price - vwap)
            slippage_bps = round((diff / arrival_price) * 10000, 2)

        report = {
            "order_id": order_id, "symbol": symbol, "side": side,
            "quantity": quantity, "limit_price": limit_price,
            "arrival_price": arrival_price, "achieved_vwap": vwap,
            "slippage_bps": slippage_bps,
            "fill_ratio": execution_result.get("fill_ratio", 0.0),
            "total_filled": total_filled,
            "routing_latency_ms": routing_decision.get("routing_latency_us", 0) / 1000.0,
            "is_split": routing_decision.get("is_split", False),
            "primary_venue": routing_decision.get("primary_venue"),
            "venues_considered": len(venue_scores), "venues_selected": len(legs),
            "best_score_venue": sorted_v[0]["venue"] if sorted_v else None,
            "alternatives_not_chosen": [
                {"venue": v["venue"], "score": v.get("score")}
                for v in sorted_v if v["venue"] not in chosen
            ][:3],
            "venue_scores": venue_scores, "legs": legs,
            "execution_reports": execution_result.get("executions", []),
            "mifid2": {
                "policy": "6-factor SOR: liquidity 28%, spread 18%, FX 18%, fee 16%, latency 10%, reliability 10%",
                "order_type": "market" if not limit_price else "limit",
                "quality_metric": "VWAP vs arrival price",
                "venue_instruction": "system-selected",
                "ts_received": execution_result.get("timestamp", time.time()),
                "ts_executed": time.time(),
            },
            "timestamp": time.time(),
        }
        with self._lock:
            if len(self._reports) >= self._max:
                self._reports = self._reports[-(self._max - 1):]
                self._index = {r["order_id"]: i for i, r in enumerate(self._reports)}
            self._index[order_id] = len(self._reports)
            self._reports.append(report)
        return report

    def get(self, order_id):
        with self._lock:
            idx = self._index.get(order_id)
            if idx is None: return None
            try: return self._reports[idx]
            except IndexError: return None

    def list(self, symbol=None, limit=100):
        with self._lock:
            res = self._reports if not symbol else [r for r in self._reports if r["symbol"] == symbol.upper()]
            return list(reversed(res[-limit:]))

    def summary(self):
        with self._lock:
            if not self._reports: return {"total": 0}
            slips = [r["slippage_bps"] for r in self._reports if r.get("slippage_bps") is not None]
            fills = [r["fill_ratio"] for r in self._reports if r.get("fill_ratio") is not None]
            return {"total": len(self._reports),
                    "avg_slippage_bps": round(sum(slips)/len(slips), 2) if slips else None,
                    "avg_fill_ratio": round(sum(fills)/len(fills), 4) if fills else None,
                    "split_pct": round(sum(1 for r in self._reports if r["is_split"])/len(self._reports)*100, 1)}
