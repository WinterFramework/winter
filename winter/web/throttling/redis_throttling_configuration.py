from dataclasses import dataclass

from .exceptions import ThrottlingMisconfigurationException


@dataclass
class RedisThrottlingConfiguration:
    host: str
    port: int
    db: int
    password: str | None = None


_redis_throttling_configuration: RedisThrottlingConfiguration | None = None


def set_redis_throttling_configuration(configuration: RedisThrottlingConfiguration):
    global _redis_throttling_configuration
    if _redis_throttling_configuration is not None:
        raise ThrottlingMisconfigurationException(f'{RedisThrottlingConfiguration.__name__} is already initialized')
    _redis_throttling_configuration = configuration


def get_redis_throttling_configuration() -> RedisThrottlingConfiguration | None:
    return _redis_throttling_configuration
