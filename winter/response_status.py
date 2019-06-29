from http import HTTPStatus
from typing import Union

import dataclasses

from .core import ComponentMethod
from .core import annotate

_default_http_method_statuses = {
    'get': HTTPStatus.OK,
    'post': HTTPStatus.OK,
    'put': HTTPStatus.OK,
    'patch': HTTPStatus.OK,
    'delete': HTTPStatus.NO_CONTENT,
}


@dataclasses.dataclass
class ResponseStatusAnnotation:
    status_code: HTTPStatus


def response_status(status: Union[HTTPStatus, int]):
    status = HTTPStatus(status)
    annotation = ResponseStatusAnnotation(status)
    return annotate(annotation, single=True)


def get_default_response_status(http_method: str, method: ComponentMethod) -> int:
    response_status_annotation = method.annotations.get_one_or_none(ResponseStatusAnnotation)
    if response_status_annotation is not None:
        return response_status_annotation.status_code.value
    status_code = _default_http_method_statuses[http_method.lower()]
    return status_code.value
