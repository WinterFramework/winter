import warnings

from .exceptions import ThrottlingMisconfigurationException
from .storage import InMemoryThrottlingStorage
from .storage import ThrottlingStorage
from .storage import get_throttling_storage
from .storage import set_throttling_storage
from .throttling import create_throttle_class
from .throttling import reset
from .throttling import throttling

_DEPRECATED_REDIS_NAMES = ('RedisThrottlingConfiguration', 'set_redis_throttling_configuration')


def __getattr__(name):
    # Deprecated since 33.0, removed in 34.0: the Redis storage lives in the winter.redis adapter.
    if name in _DEPRECATED_REDIS_NAMES:
        warnings.warn(
            f'winter.web.throttling.{name} is deprecated, use winter.redis.throttling.{name}',
            DeprecationWarning,
            stacklevel=2,
        )
        from winter.redis import throttling as redis_throttling
        return getattr(redis_throttling, name)
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
