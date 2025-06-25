from redis import Redis
from redis.commands.core import Script

from .exceptions import ThrottlingMisconfigurationException
from .redis_throttling_configuration import get_redis_throttling_configuration

# Redis Lua scripts are atomic
# Sliding window throttling.
# Rejected requests aren't counted.
RATE_LIMIT_LUA = '''
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

_redis_throttling_client: Redis | None = None
_rate_limit_script: Script | None = None

def get_redis_throttling_client() -> tuple[Redis, Script]:
    global _redis_throttling_client
    global _rate_limit_script

    if _redis_throttling_client is None:
        configuration = get_redis_throttling_configuration()

        if configuration is None:
            raise ThrottlingMisconfigurationException('Configuration for Redis must be set before using the throttling')

        _redis_throttling_client = Redis(
            host=configuration.host,
            port=configuration.port,
            db=configuration.db,
            password=configuration.password,
            decode_responses=True,
        )

        _rate_limit_script = _redis_throttling_client.register_script(RATE_LIMIT_LUA)
    return _redis_throttling_client, _rate_limit_script
