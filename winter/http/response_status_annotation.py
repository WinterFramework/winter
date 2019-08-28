from http import HTTPStatus
from typing import Union

import dataclasses

from ..core import annotate


@dataclasses.dataclass
class ResponseStatusAnnotation:
    status_code: HTTPStatus


def response_status(status: Union[HTTPStatus, int]):
    status = HTTPStatus(status)
    annotation = ResponseStatusAnnotation(status)
    return annotate(annotation, single=True)
