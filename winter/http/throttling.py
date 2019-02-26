import dataclasses
from rest_framework.throttling import ScopedRateThrottle

from ..core import annotate


@dataclasses.dataclass
class ThrottlingAnnotation:
    rate: str


def throttling(rate: str):
    return annotate(ThrottlingAnnotation(rate), single=True)


class WinterRateThrottle(ScopedRateThrottle):

    def allow_request(self, request, view):

        rate = self._get_rate(request, view)
        if rate is None:
            return True

        self.num_requests, self.duration = self.parse_rate(rate)

        self.key = self.get_cache_key(request, view)

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return self.throttle_success()

    def _get_rate(self, request, view):
        controller_cls = type(view)

        func = getattr(controller_cls, request.method.lower(), None)
        method = getattr(func, 'method', None)

        if method is None:
            return True

        throttling_annotation = method.annotations.get_one_or_none(ThrottlingAnnotation)

        if throttling_annotation is not None:
            return throttling_annotation.rate

        throttling_annotation = method.component.annotations.get_one_or_none(ThrottlingAnnotation)

        if throttling_annotation is not None:
            return throttling_annotation.rate
        return None
