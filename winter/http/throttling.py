import time
import typing
import uuid

import dataclasses
from django.core.cache import cache as default_cache
from rest_framework.throttling import BaseThrottle

from ..core import Component
from ..core import annotate

if typing.TYPE_CHECKING:
    from ..routing import Route  # noqa: F401


@dataclasses.dataclass
class ThrottlingAnnotation:
    rate: typing.Optional[str]
    scope: typing.Optional[str]


@dataclasses.dataclass
class Throttling:
    num_requests: int
    duration: int
    scope: str


def throttling(rate: typing.Optional[str], scope: typing.Optional[str] = None):
    if scope is None:
        scope = uuid.uuid4()
    return annotate(ThrottlingAnnotation(rate, scope), single=True)


class BaseRateThrottle(BaseThrottle):
    throttling_by_http_method: typing.Dict[str, Throttling] = {}
    cache = default_cache
    cache_format = 'throttle_{scope}_{ident}'

    def allow_request(self, request, view) -> bool:
        throttling_ = self._get_throttling(request)

        if throttling_ is None:
            return True

        ident = self.get_ident(request)
        key = self._get_cache_key(throttling_.scope, ident)

        history = self.cache.get(key, [])
        now = time.time()

        while history and history[-1] <= now - throttling_.duration:
            history.pop()

        if len(history) >= throttling_.num_requests:
            return False

        history.insert(0, now)
        self.cache.set(key, history, throttling_.duration)
        return True

    def _get_cache_key(self, scope: str, ident: str) -> str:
        return self.cache_format.format(scope=scope, ident=ident)

    def get_ident(self, request) -> str:
        user_pk = request.user.pk if request.user.is_authenticated else None

        if user_pk is not None:
            return str(user_pk)
        return super().get_ident(request)

    def _get_throttling(self, request) -> typing.Optional[Throttling]:
        return self.throttling_by_http_method.get(request.method.lower())


def _parse_rate(rate: str) -> typing.Tuple[int, int]:
    """
    Given the request rate string, return a two tuple of:
    <allowed number of requests>, <period of time in seconds>
    """
    num, period = rate.split('/')
    num_requests = int(num)
    duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
    return num_requests, duration


def create_throttle_classes(
        component: Component,
        routes: typing.List['Route'],
) -> typing.Tuple[typing.Type[BaseRateThrottle], ...]:
    base_throttling_annotation = component.annotations.get_one_or_none(ThrottlingAnnotation)
    throttling_by_http_method_: typing.Dict[str, Throttling] = {}

    for route in routes:

        throttling_annotation = (
            route.method.annotations.get_one_or_none(ThrottlingAnnotation) or base_throttling_annotation
        )

        if getattr(throttling_annotation, 'rate', None) is not None:
            num_requests, duration = _parse_rate(throttling_annotation.rate)
            throttling_ = Throttling(num_requests, duration, throttling_annotation.scope)
            throttling_by_http_method_[route.http_method.lower()] = throttling_

    if not throttling_by_http_method_:
        return ()

    class RateThrottle(BaseRateThrottle):
        throttling_by_http_method = throttling_by_http_method_

    return (RateThrottle,)
