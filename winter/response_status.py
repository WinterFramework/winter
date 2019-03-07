import dataclasses

from .core import ComponentMethod
from .core import annotate

_default_http_method_statuses = {
    'get': 200,
    'post': 200,
    'put': 200,
    'patch': 200,
    'delete': 204,
}


@dataclasses.dataclass
class ResponseStatusAnnotation:
    status_code: int


def response_status(status: int):
    annotation = ResponseStatusAnnotation(status)
    return annotate(annotation, single=True)


def get_default_response_status(http_method: str, method: ComponentMethod) -> int:
    response_status_annotation = method.annotations.get_one_or_none(ResponseStatusAnnotation)
    if response_status_annotation is not None:
        return response_status_annotation.status_code
    return _default_http_method_statuses.get(http_method.lower())
