"""
Thread-safe bounded order history store.
Keeps the most recent maxsize orders; oldest evicted when full.
"""
import threading
from collections import OrderedDict
from typing import Optional


class OrderStore:
    def __init__(self, maxsize: int = 10_000):
        self._data: OrderedDict = OrderedDict()
        self._lock = threading.Lock()
        self._maxsize = maxsize

    def save(self, order_id: str, data: dict):
        with self._lock:
            self._data[order_id] = data
            if len(self._data) > self._maxsize:
                self._data.popitem(last=False)

    def get(self, order_id: str) -> Optional[dict]:
        with self._lock:
            return self._data.get(order_id)

    def recent(self, limit: int = 50) -> list:
        with self._lock:
            items = list(self._data.values())
        return list(reversed(items[-limit:]))  # newest-first

    def count(self) -> int:
        with self._lock:
            return len(self._data)
