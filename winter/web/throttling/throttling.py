import dataclasses
from typing import Optional
from typing import TYPE_CHECKING
from typing import Tuple


from winter.web.request import Request
from winter.components import annotate_method
from .identity import get_throttling_identity
from .storage import get_throttling_storage

if TYPE_CHECKING:
    from winter.web.routing import Route  # noqa: F401


@dataclasses.dataclass
class ThrottlingAnnotation:
    rate: Optional[str]
    scope: Optional[str]


@dataclasses.dataclass
class Throttling:
    num_requests: int
    duration: int
    scope: str


def throttling(rate: Optional[str], scope: Optional[str] = None):
    return annotate_method(ThrottlingAnnotation(rate, scope), single=True)


class BaseRateThrottle:
    def __init__(self, throttling_: Throttling):
        self._throttling = throttling_
        self._storage = get_throttling_storage()

    def allow_request(self, request: Request) -> bool:
        ident = get_throttling_identity(request)
        key = _get_cache_key(self._throttling.scope, ident)

        return self._storage.is_request_allowed(key, self._throttling.duration, self._throttling.num_requests)


def reset(request: Request, scope: str):
    """
        This function allows to reset the accumulated throttling state
        for a specific user and scope
    """
    ident = get_throttling_identity(request)
    key = _get_cache_key(scope, ident)
    get_throttling_storage().delete(key)


CACHE_KEY_FORMAT = 'throttle_{scope}_{ident}'


def _get_cache_key(scope: str, ident: str) -> str:
    return CACHE_KEY_FORMAT.format(scope=scope, ident=ident)


def _parse_rate(rate: str) -> Tuple[int, int]:
    """
    Given the request rate string, return a two tuple of:
    <allowed number of requests>, <period of time in seconds>
    """
    num, period = rate.split('/')
    num_requests = int(num)
    duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
    return num_requests, duration


def create_throttle_class(route: 'Route') -> Optional[BaseRateThrottle]:
    throttling_annotation = route.method.annotations.get_one_or_none(ThrottlingAnnotation)

    if getattr(throttling_annotation, 'rate', None) is None:
        return None

    num_requests, duration = _parse_rate(throttling_annotation.rate)
    throttling_scope = throttling_annotation.scope or route.method.full_name
    throttling_ = Throttling(num_requests, duration, throttling_scope)

    return BaseRateThrottle(throttling_)
