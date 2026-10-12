import abc
import threading
import time
from collections import defaultdict
from collections import deque

from .exceptions import ThrottlingMisconfigurationException


class ThrottlingStorage(abc.ABC):
    """
    Sliding-window request counter. Implementations live in adapters (see winter.redis.throttling);
    InMemoryThrottlingStorage below is for single-process deployments and tests.
    """

    @abc.abstractmethod
    def is_request_allowed(self, key: str, duration: int, num_requests: int) -> bool:  # pragma: no cover
        """Record a request under `key` unless more than `num_requests` happened within the last `duration` seconds."""

    @abc.abstractmethod
    def delete(self, key: str):  # pragma: no cover
        """Forget all requests recorded under `key`."""


class InMemoryThrottlingStorage(ThrottlingStorage):
    def __init__(self):
        self._timestamps: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def is_request_allowed(self, key: str, duration: int, num_requests: int) -> bool:
        now = time.time()
        with self._lock:
            window = self._timestamps[key]
            while window and window[0] <= now - duration:
                window.popleft()
            if len(window) >= num_requests:
                return False
            window.append(now)
            return True

    def delete(self, key: str):
        with self._lock:
            self._timestamps.pop(key, None)


_throttling_storage: ThrottlingStorage | None = None


def set_throttling_storage(storage: ThrottlingStorage):
    global _throttling_storage
    _throttling_storage = storage


def get_throttling_storage() -> ThrottlingStorage:
    if _throttling_storage is None:
        raise ThrottlingMisconfigurationException('Throttling storage must be set before using the throttling')
    return _throttling_storage
