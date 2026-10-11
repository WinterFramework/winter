import time
import warnings
from dataclasses import dataclass
from typing import Optional

from redis import Redis

from winter.web.throttling import ThrottlingStorage
from winter.web.throttling import set_throttling_storage


@dataclass
class RedisThrottlingConfiguration:
    host: str
    port: int
    db: int
    password: Optional[str] = None


class RedisThrottlingStorage(ThrottlingStorage):
    # Redis Lua scripts are atomic
    # Sliding window throttling.
    # Rejected requests aren't counted.
    THROTTLING_LUA = '''
    local key = KEYS[1]
    local now = tonumber(ARGV[1])
    local duration = tonumber(ARGV[2])
    local max_requests = tonumber(ARGV[3])

    redis.call("ZREMRANGEBYSCORE", key, 0, now - duration)
    local count = redis.call("ZCARD", key)

    if count >= max_requests then
        return 0
    end

    redis.call("ZADD", key, now, now)
    redis.call("EXPIRE", key, duration)
    return 1
    '''

    def __init__(self, configuration: RedisThrottlingConfiguration):
        self._redis_client = Redis(
            host=configuration.host,
            port=configuration.port,
            db=configuration.db,
            password=configuration.password,
            decode_responses=True,
        )
        self._throttling_script = self._redis_client.register_script(self.THROTTLING_LUA)

    def is_request_allowed(self, key: str, duration: int, num_requests: int) -> bool:
        now = time.time()
        is_allowed = self._throttling_script(
            keys=[key],
            args=[now, duration, num_requests],
        )
        return is_allowed == 1

    def delete(self, key: str):
        self._redis_client.delete(key)


def set_redis_throttling_configuration(configuration: RedisThrottlingConfiguration):
    """Deprecated since 33.0, removed in 34.0. Use set_throttling_storage(RedisThrottlingStorage(configuration))."""
    warnings.warn(
        'set_redis_throttling_configuration is deprecated, '
        'use winter.web.throttling.set_throttling_storage(RedisThrottlingStorage(configuration))',
        DeprecationWarning,
        stacklevel=2,
    )
    set_throttling_storage(RedisThrottlingStorage(configuration))
