"""
Monitoring and observability — lightweight in-process metrics.
Exports Prometheus-compatible text format at /metrics endpoint.
In production: swap for prometheus_client library.
"""
import threading
from collections import defaultdict, deque
from typing import Dict


class MetricsRegistry:
    def __init__(self):
        self._counters:   Dict[str, float]  = defaultdict(float)
        self._gauges:     Dict[str, float]  = defaultdict(float)
        self._histograms: Dict[str, deque]  = defaultdict(lambda: deque(maxlen=10_000))
        self._lock = threading.Lock()

    def inc(self, name: str, value: float = 1.0, **labels):
        key = _label_key(name, labels)
        with self._lock:
            self._counters[key] += value

    def set_gauge(self, name: str, value: float, **labels):
        key = _label_key(name, labels)
        with self._lock:
            self._gauges[key] = value

    def observe(self, name: str, value: float, **labels):
        key = _label_key(name, labels)
        with self._lock:
            self._histograms[key].append(value)

    def percentile(self, name: str, p: float, **labels) -> float:
        key = _label_key(name, labels)
        with self._lock:
            dq  = self._histograms.get(key)
            raw = list(dq) if dq else []
        if not raw:
            return 0.0
        data = sorted(raw)
        return data[int((len(data) - 1) * p)]

    def prometheus_text(self) -> str:
        # Copy all data under the lock; all sorting and formatting happen outside it.
        with self._lock:
            counters = list(self._counters.items())
            gauges   = list(self._gauges.items())
            hist_raw = {k: list(dq) for k, dq in self._histograms.items()}

        lines: list = []
        seen_types: set = set()
        for k, v in counters:
            base = k.split("{")[0]
            if base not in seen_types:
                lines.append(f"# TYPE {base} counter")
                seen_types.add(base)
            lines.append(f"{k} {v}")
        for k, v in gauges:
            base = k.split("{")[0]
            if base not in seen_types:
                lines.append(f"# TYPE {base} gauge")
                seen_types.add(base)
            lines.append(f"{k} {v}")
        for k, raw in hist_raw.items():
            base   = k.split("{")[0]
            labels = k[len(base):]  # e.g. '{venue="GSE"}' or ''
            data   = sorted(raw)
            if data:
                if base not in seen_types:
                    lines.append(f"# TYPE {base} histogram")
                    seen_types.add(base)
                lines.append(f"{base}_count{labels} {len(data)}")
                lines.append(f"{base}_p50{labels} {_pct(data, 0.50)}")
                lines.append(f"{base}_p95{labels} {_pct(data, 0.95)}")
                lines.append(f"{base}_p99{labels} {_pct(data, 0.99)}")
        return "\n".join(lines)

    def snapshot(self) -> dict:
        with self._lock:
            counters  = dict(self._counters)
            gauges    = dict(self._gauges)
            hist_raw  = {k: list(dq) for k, dq in self._histograms.items()}
        hists = {}
        for k, raw in hist_raw.items():
            data = sorted(raw)
            hists[k] = {
                "count": len(data),
                "p50":   _pct(data, 0.50),
                "p95":   _pct(data, 0.95),
                "p99":   _pct(data, 0.99),
            }
        return {"counters": counters, "gauges": gauges, "histograms": hists}


def _label_key(name: str, labels: dict) -> str:
    if not labels:
        return name
    parts = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
    return f"{name}{{{parts}}}"


def _pct(data: list, p: float) -> float:
    if not data:
        return 0.0
    return data[int((len(data) - 1) * p)]


# Global singleton
metrics = MetricsRegistry()
