import warnings
from http import HTTPStatus
from typing import Optional

import dataclasses

from winter.core import annotate
from ..exceptions import problem


@problem(HTTPStatus.BAD_REQUEST)
class MaximumLimitValueExceeded(Exception):
    def __init__(self, maximum_limit: int):
        super().__init__(f'Maximum limit value is exceeded: {maximum_limit}')


@dataclasses.dataclass(frozen=True)
class Limits:
    default: Optional[int]
    maximum: Optional[int]
    redirect_to_default: bool

    def __post_init__(self):
        if self.redirect_to_default and self.default is None:
            warnings.warn(
                'PagePositionArgumentResolver: redirect_to_default_limit is set to True, '
                'however it has no effect as default_limit is not specified',
                UserWarning,
            )


@dataclasses.dataclass(frozen=True)
class LimitsAnnotation:
    limits: Limits


def limits(*, default: Optional[int], maximum: Optional[int], redirect_to_default: bool = False):
    limits_ = Limits(default=default, maximum=maximum, redirect_to_default=redirect_to_default)
    annotation = LimitsAnnotation(limits_)
    return annotate(annotation, single=True)
