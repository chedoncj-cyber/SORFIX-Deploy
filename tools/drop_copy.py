"""FIX Drop Copy — real-time copy of all order flow to compliance endpoints."""
import json, logging, threading, time
from typing import List
from urllib import request as urlreq
from urllib.error import URLError

logger = logging.getLogger("drop_copy")


class DropCopyEngine:
    def __init__(self, max_log: int = 500):
        self._endpoints: list = []; self._log: list = []
        self._lock = threading.Lock(); self._max_log = max_log

    def register(self, url, label="", enabled=True):
        with self._lock:
            for ep in self._endpoints:
                if ep["url"] == url:
                    ep["label"] = label; ep["enabled"] = enabled; return ep
            ep = {"url": url, "label": label, "enabled": enabled, "registered_at": time.time()}
            self._endpoints.append(ep); return ep

    def remove(self, url):
        with self._lock:
            before = len(self._endpoints)
            self._endpoints = [e for e in self._endpoints if e["url"] != url]
            return len(self._endpoints) < before

    def list_endpoints(self):
        with self._lock: return list(self._endpoints)

    def send(self, order_data, event="ORDER_SUBMITTED"):
        payload = {"event": event, "timestamp": time.time(), "data": order_data}
        with self._lock:
            endpoints = [e for e in self._endpoints if e.get("enabled")]
        for ep in endpoints:
            threading.Thread(target=self._post, args=(ep["url"], payload), daemon=True).start()
        self._log_entry(event, order_data, len(endpoints))

    def _post(self, url, payload):
        try:
            body = json.dumps(payload).encode()
            req = urlreq.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
            with urlreq.urlopen(req, timeout=5) as r:
                logger.debug("Drop copy → %s: %s", url, r.status)
        except Exception as e:
            logger.warning("Drop copy failed → %s: %s", url, e)

    def _log_entry(self, event, data, n_endpoints):
        with self._lock:
            routing = data.get("routing") or {}
            entry = {"event": event,
                     "order_id": data.get("order_id"),
                     "symbol": routing.get("symbol") if isinstance(routing, dict) else None,
                     "side": data.get("side"),
                     "timestamp": time.time(),
                     "endpoints_notified": n_endpoints}
            self._log.append(entry)
            if len(self._log) > self._max_log: self._log = self._log[-self._max_log:]

    def get_log(self, limit=100):
        with self._lock: return list(reversed(self._log[-limit:]))

    def stats(self):
        with self._lock:
            return {"endpoints": len(self._endpoints),
                    "enabled": sum(1 for e in self._endpoints if e.get("enabled")),
                    "copies_sent": len(self._log)}
