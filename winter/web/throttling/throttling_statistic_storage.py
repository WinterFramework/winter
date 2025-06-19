from contextlib import contextmanager
from typing import Generator

from redis import Redis
from redis.exceptions import LockError
from redis.exceptions import LockNotOwnedError

from .redis_throttling_configuration import RedisThrottlingConfiguration


class ThrottlingStatisticStorage:
    def __init__(self, configuration: RedisThrottlingConfiguration):
        self._redis_client = Redis(
            host=configuration.host,
            port=configuration.port,
            db=configuration.db,
            password=configuration.password,
            decode_responses=True,
        )

    @contextmanager
    def lock(self, key: str, timeout_sec: int) -> Generator[None, None, None]:
        lock = self._redis_client.lock(f'lock:{key}', timeout=timeout_sec, blocking=True)
        lock.acquire()

        try:
            yield
        finally:
            try:
                lock.release()
            except (LockError, LockNotOwnedError):
                pass

    def get(self, key: str) -> list[float]:
        raw_value: str | None  = self._redis_client.get(key)
        if raw_value is None:
            return []

        value = map(float, raw_value.split(','))
        return list(value)

    def set(self, key: str, value: list[float], ex: int):
        raw_value = ','.join(map(str, value))
        self._redis_client.set(key, raw_value, ex)

    def delete(self, key: str):
        self._redis_client.delete(key)


_throttling_statistic_storage: ThrottlingStatisticStorage | None = None


def init_throttling_statistic_storage(configuration: RedisThrottlingConfiguration):
    global _throttling_statistic_storage
    if _throttling_statistic_storage is not None:
        raise RuntimeError("ThrottlingStatisticStorage is already initialized.")
    _throttling_statistic_storage = ThrottlingStatisticStorage(configuration)


def get_throttling_statistic_storage() -> ThrottlingStatisticStorage:
    if _throttling_statistic_storage is None:
        raise RuntimeError("ThrottlingStatisticStorage is not initialized.")
    return _throttling_statistic_storage