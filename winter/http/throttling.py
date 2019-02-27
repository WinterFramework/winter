import time
import typing

import dataclasses
from django.core.cache import cache as default_cache
from rest_framework.throttling import BaseThrottle

from ..core import Component
from ..core import annotate

if typing.TYPE_CHECKING:  # pragma: no cover
    from ..routing import Route


@dataclasses.dataclass
class ThrottlingAnnotation:
    rate: str


def throttling(rate: str):
    return annotate(ThrottlingAnnotation(rate), single=True)


class BaseRateThrottle(BaseThrottle):
    rate_by_http_method = {}
    cache = default_cache
    cache_format = 'throttle_{scope}_{ident}'
    scope = None

    def allow_request(self, request, view):
        self.rate = self._get_rate(request)

        if self.rate is None:
            return True

        num_requests, duration = self.parse_rate(self.rate)

        self.key = self.get_cache_key(request, view)

        history = self.cache.get(self.key, [])
        self.now = time.time()

        while history and history[-1] <= self.now - duration:
            history.pop()
        if len(history) >= num_requests:
            return False

        history.insert(0, self.now)
        self.cache.set(self.key, history, duration)
        return True

    def parse_rate(self, rate):
        """
        Given the request rate string, return a two tuple of:
        <allowed number of requests>, <period of time in seconds>
        """
        if rate is None:
            return (None, None)
        num, period = rate.split('/')
        num_requests = int(num)
        duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
        return (num_requests, duration)

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format.format(scope=self.scope, ident=ident)

    def _get_rate(self, request):
        return self.rate_by_http_method.get(request.method.lower())


def create_throttle_classes(
        component: Component,
        routes: typing.List['Route'],
) -> typing.Tuple[typing.Type[BaseRateThrottle], ...]:
    throttling_annotation = component.annotations.get_one_or_none(ThrottlingAnnotation)
    base_rate = throttling_annotation.rate if throttling_annotation is not None else None
    rate_by_http_method_ = {}

    for route in routes:

        throttling_annotation = route.method.annotations.get_one_or_none(ThrottlingAnnotation)

        rate = throttling_annotation.rate if throttling_annotation is not None else base_rate

        rate_by_http_method_[route.http_method.lower()] = rate

    rate_by_http_method_ = {key: value for key, value in rate_by_http_method_.items() if value is not None}

    if not rate_by_http_method_:
        return ()

    class RateThrottle(BaseRateThrottle):
        rate_by_http_method = rate_by_http_method_
        scope = component.component_cls.__name__

    return (RateThrottle,)
