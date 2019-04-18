import typing
from http import HTTPStatus

import dataclasses
from rest_framework.request import Request
from rest_framework.response import Response

from ..core import annotate
from ..exceptions.handlers import ExceptionHandler


class MaximumLimitValueExceeded(Exception):
    def __init__(self, maximum_limit: int):
        super().__init__(f'Maximum limit value is exceeded: {maximum_limit}')


class RedirectToDefaultLimitException(Exception):
    def __init__(self, redirect_to: str):
        super().__init__()
        self.redirect_to = redirect_to


class RedirectToDefaultLimitExceptionHandler(ExceptionHandler):
    def handle(self, request: Request, exception: Exception):
        assert isinstance(exception, RedirectToDefaultLimitException)
        return Response(status=HTTPStatus.FOUND, headers={'Location': exception.redirect_to})


@dataclasses.dataclass(frozen=True)
class LimitsAnnotation:
    default: typing.Optional[int]
    maximum: typing.Optional[int]
    redirect_to_default: bool


def limits(
        *,
        default: typing.Optional[int],
        maximum: typing.Optional[int],
        redirect_to_default: bool = False,
):
    annotation = LimitsAnnotation(default=default, maximum=maximum, redirect_to_default=redirect_to_default)
    return annotate(annotation, single=True)
