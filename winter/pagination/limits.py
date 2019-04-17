import dataclasses


@dataclasses.dataclass(frozen=True)
class LimitsAnnotation:
    default: int
    maximum: int


def limits(default: int, maximum: int):
    annotation = LimitsAnnotation(default=default, maximum=maximum)
    return annotation
