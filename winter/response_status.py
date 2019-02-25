import typing

import dataclasses

from .core import annotate

if typing.TYPE_CHECKING:  # pragma: no cover
    from .routing import Route

_default_http_method_statuses = {
    'get': 200,
    'post': 200,
    'patch': 200,
    'delete': 204,
}


@dataclasses.dataclass
class ResponseStatusAnnotation:
    status_code: int


def response_status(status: int):
    annotation = ResponseStatusAnnotation(status)
    return annotate(annotation, single=True)


def get_default_response_status(route: 'Route') -> int:
    method = route.method
    response_status_annotation = method.annotations.get_one_or_none(ResponseStatusAnnotation)
    if response_status_annotation is not None:
        return response_status_annotation.status_code
    return _default_http_method_statuses.get(route.http_method.lower())
