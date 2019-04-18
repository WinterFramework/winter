import typing

import dataclasses

from ..core import annotate


class MaximumLimitValueExceeded(Exception):
    def __init__(self, maximum_limit: int):
        super().__init__(f'Maximum limit value is exceeded: {maximum_limit}')


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
