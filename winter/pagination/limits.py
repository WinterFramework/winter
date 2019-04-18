import typing

import dataclasses

from ..core import annotate


@dataclasses.dataclass(frozen=True)
class LimitsAnnotation:
    default: typing.Optional[int]
    maximum: typing.Optional[int]


def limits(default: typing.Optional[int], maximum: typing.Optional[int]):
    annotation = LimitsAnnotation(default=default, maximum=maximum)
    return annotate(annotation, single=True)
