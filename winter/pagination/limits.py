import typing

import dataclasses


@dataclasses.dataclass(frozen=True)
class LimitsAnnotation:
    default: typing.Optional[int]
    maximum: typing.Optional[int]


def limits(default: typing.Optional[int], maximum: typing.Optional[int]):
    annotation = LimitsAnnotation(default=default, maximum=maximum)
    return annotation
