import dataclasses
from rest_framework.throttling import SimpleRateThrottle

from ..core import Component
from ..core import annotate


@dataclasses.dataclass
class ThrottlingAnnotation:
    rate: str


def throttling(rate: str):
    return annotate(ThrottlingAnnotation(rate))


class WinterRateThrottle(SimpleRateThrottle):

    def get_cache_key(self, request, view):
        """
        If `view.throttle_scope` is not set, don't apply this throttle.

        Otherwise generate the unique cache key by concatenating the user id
        with the '.throttle_scope` property of the view.
        """
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

    def allow_request(self, request, view):
        controller_cls = type(view)
        component = Component.get_by_cls(controller_cls)
        throttling_annotations = component.annotations.get(ThrottlingAnnotation)

        if not throttling_annotations:
            return True
        throttling_annotation = throttling_annotations[0]

        self.num_requests = throttling_annotation.num_requests
        self.duration = throttling_annotation.duration

        # We can now proceed as normal.
        return super().allow_request(request, view)
