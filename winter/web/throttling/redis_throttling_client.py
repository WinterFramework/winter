from redis import Redis

from .redis_throttling_configuration import get_redis_throttling_configuration

_redis_throttling_client: Redis | None = None

def get_redis_throttling_client() -> Redis:
    global _redis_throttling_client
    if _redis_throttling_client is None:
        configuration = get_redis_throttling_configuration()

        if configuration is None:
            raise RuntimeError(f'Configuration for Redis must be set before using the throttling')

        _redis_throttling_client = Redis(
            host=configuration.host,
            port=configuration.port,
            db=configuration.db,
            password=configuration.password,
            decode_responses=True,
        )
    return _redis_throttling_client
