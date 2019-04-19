import typing

import dataclasses

from ..core import annotate


class MaximumLimitValueExceeded(Exception):
    def __init__(self, maximum_limit: int):
        super().__init__(f'Maximum limit value is exceeded: {maximum_limit}')


@dataclasses.dataclass(frozen=True)
class Limits:
    default: typing.Optional[int]
    maximum: typing.Optional[int]
    redirect_to_default: bool


@dataclasses.dataclass(frozen=True)
class LimitsAnnotation:
    limits: Limits


def limits(
        *,
        default: typing.Optional[int],
        maximum: typing.Optional[int],
        redirect_to_default: bool = False,
):
    limits_ = Limits(default=default, maximum=maximum, redirect_to_default=redirect_to_default)
    annotation = LimitsAnnotation(limits_)
    return annotate(annotation, single=True)
