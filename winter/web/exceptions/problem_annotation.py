from http import HTTPStatus

from dataclasses import dataclass


@dataclass(frozen=True)
class ProblemAnnotation:
    status: HTTPStatus
    title: str
    detail: str
    type: str
