import dataclasses
from typing import Optional
from typing import Tuple

from injector import Injector

from winter.web.request import Request
from winter.components import ComponentMethod
from winter.components import annotate_method
from .identity import IdentityResolver
from .storage import ThrottlingStorage


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


class Throttle:
    """
    The throttling of one request in the scope of its API method. An API method with @throttling receives it as an
    argument to reset what is counted for whoever sends the request.
    """

    def __init__(
        self,
        throttling_: Throttling,
        storage: ThrottlingStorage,
        request: Request,
        identity: IdentityResolver,
    ):
        self._throttling = throttling_
        self._storage = storage
        self._request = request
        self._identity = identity
        self._key: Optional[str] = None

    def allow_request(self) -> bool:
        """Count the request unless the scope has reached its rate for whoever sends it."""
        self._key = _get_cache_key(self._throttling.scope, self._identity(self._request))
        return self._storage.is_request_allowed(self._key, self._throttling.duration, self._throttling.num_requests)

    def reset(self):
        """
        Forget the requests counted in the scope for whoever sends the request, this one included. The identity is
        the one the request was counted for, even if the API method has logged the user in since.
        """
        self._storage.delete(self._key)


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


def get_throttling(method: ComponentMethod) -> Optional[Throttling]:
    throttling_annotation = method.annotations.get_one_or_none(ThrottlingAnnotation)

    if getattr(throttling_annotation, 'rate', None) is None:
        return None

    num_requests, duration = _parse_rate(throttling_annotation.rate)
    throttling_scope = throttling_annotation.scope or method.full_name
    return Throttling(num_requests, duration, throttling_scope)


def create_throttle(
    method: ComponentMethod,
    request: Request,
    app_injector: Injector,
    identity: IdentityResolver,
) -> Optional[Throttle]:
    """The throttle of a request to the method, counting in the storage that the injector of the application binds."""
    throttling_ = get_throttling(method)
    if throttling_ is None:
        return None
    return Throttle(throttling_, app_injector.get(ThrottlingStorage), request, identity)
