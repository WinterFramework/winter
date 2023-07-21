import dataclasses
import time
from typing import Optional
from typing import TYPE_CHECKING
from typing import Tuple

import django.http
from django.core.cache import cache as default_cache

from winter.core import annotate_method

if TYPE_CHECKING:
    from .routing import Route  # noqa: F401


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

    def allow_request(self, request: django.http.HttpRequest) -> bool:
        ident = _get_ident(request)
        key = _get_cache_key(self._throttling.scope, ident)

        history = default_cache.get(key, [])
        now = time.time()

        while history and history[-1] <= now - self._throttling.duration:
            history.pop()

        if len(history) >= self._throttling.num_requests:
            return False

        history.insert(0, now)
        default_cache.set(key, history, self._throttling.duration)
        return True


def reset(request: django.http.HttpRequest, scope: str):
    """
        This function allows to reset the accumulated throttling state
        for a specific user and scope
    """
    ident = _get_ident(request)
    key = _get_cache_key(scope, ident)
    default_cache.delete(key)


CACHE_KEY_FORMAT = 'throttle_{scope}_{ident}'


def _get_cache_key(scope: str, ident: str) -> str:
    return CACHE_KEY_FORMAT.format(scope=scope, ident=ident)


def _get_ident(request: django.http.HttpRequest) -> str:
    if hasattr(request, 'user') and request.user.is_authenticated:
        return str(request.user.pk)

    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    remote_addr = request.META.get('REMOTE_ADDR')
    return ''.join(xff.split()) if xff else remote_addr


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
