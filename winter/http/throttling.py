import typing

import dataclasses
from rest_framework.throttling import SimpleRateThrottle

from ..core import Component
from ..core import annotate

if typing.TYPE_CHECKING:  # pragma: no cover
    from ..routing import Route


@dataclasses.dataclass
class ThrottlingAnnotation:
    rate: str


def throttling(rate: str):
    return annotate(ThrottlingAnnotation(rate), single=True)


class BaseRateThrottle(SimpleRateThrottle):
    rate_by_http_method = {}

    def __init__(self):
        # We do not need base implementation
        pass

    def allow_request(self, request, view):
        self.rate = self._get_rate(request)

        if self.rate is None:
            return True

        self.num_requests, self.duration = self.parse_rate(self.rate)

        self.key = self.get_cache_key(request, view)

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return False
        return self.throttle_success()

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

    def _get_rate(self, request):
        return self.rate_by_http_method.get(request.method.lower())


def create_throttle_classes(
        component: Component,
        routes: typing.List['Route']
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

    return (RateThrottle,)
