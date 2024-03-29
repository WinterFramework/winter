from http import HTTPStatus

from ..core import ComponentMethod
from .response_status_annotation import ResponseStatusAnnotation

_default_http_method_statuses = {
    'get': HTTPStatus.OK,
    'post': HTTPStatus.OK,
    'put': HTTPStatus.OK,
    'patch': HTTPStatus.OK,
    'delete': HTTPStatus.NO_CONTENT,
}


def get_response_status(http_method: str, method: ComponentMethod) -> int:
    response_status_annotation = method.annotations.get_one_or_none(ResponseStatusAnnotation)
    if response_status_annotation is not None:
        return response_status_annotation.status_code.value
    status_code = _default_http_method_statuses[http_method.lower()]
    return status_code.value
