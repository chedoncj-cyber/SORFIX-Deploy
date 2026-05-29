"""
Circuit breaker pattern for exchange connectivity.
Three states: CLOSED (normal), OPEN (tripped), HALF_OPEN (probing).
"""
import threading
import time
from enum import Enum
from dataclasses import dataclass


class CBState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: float = 30.0


class CircuitBreaker:
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CBState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._lock = threading.RLock()  # RLock allows get_stats() to re-enter via state property

    @property
    def state(self) -> CBState:
        with self._lock:
            if self._state == CBState.OPEN:
                if time.time() - self._last_failure_time >= self.config.timeout_seconds:
                    self._state = CBState.HALF_OPEN
                    self._failure_count = 0  # reset so each probe window starts fresh
                    self._success_count = 0
            return self._state

    def allow(self) -> bool:
        return self.state != CBState.OPEN

    def record_success(self):
        with self._lock:
            if self._state == CBState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._state = CBState.CLOSED
                    self._failure_count = 0
            elif self._state == CBState.CLOSED:
                self._failure_count = max(0, self._failure_count - 1)

    def record_failure(self):
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            # Any failure in HALF_OPEN immediately re-trips; in CLOSED trip at threshold.
            if self._state == CBState.HALF_OPEN or self._failure_count >= self.config.failure_threshold:
                self._state = CBState.OPEN
                self._success_count = 0

    def call(self, fn):
        if not self.allow():
            raise RuntimeError(f"CircuitBreaker [{self.name}] is OPEN — exchange unreachable")
        try:
            result = fn()
            self.record_success()
            return result
        except Exception:
            self.record_failure()
            raise

    def get_stats(self) -> dict:
        with self._lock:
            return {
                "name": self.name,
                "state": self.state.value,  # RLock allows re-entry from within this lock
                "failure_count": self._failure_count,
                "success_count": self._success_count,
            }
