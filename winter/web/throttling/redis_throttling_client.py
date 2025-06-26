import time

from redis import Redis

from .exceptions import ThrottlingMisconfigurationException
from .redis_throttling_configuration import get_redis_throttling_configuration
from .redis_throttling_configuration import RedisThrottlingConfiguration


class RedisThrottlingClient:
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
            args=[now, duration, num_requests]
        )
        return is_allowed == 1

    def delete(self, key: str):
        self._redis_client.delete(key)


_redis_throttling_client: RedisThrottlingClient | None = None

def get_redis_throttling_client() -> RedisThrottlingClient:
    global _redis_throttling_client

    if _redis_throttling_client is None:
        configuration = get_redis_throttling_configuration()

        if configuration is None:
            raise ThrottlingMisconfigurationException('Configuration for Redis must be set before using the throttling')

        _redis_throttling_client = RedisThrottlingClient(configuration)

    return _redis_throttling_client
