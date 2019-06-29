import typing

import dataclasses

if typing.TYPE_CHECKING:
    from .sort import Sort  # noqa: F401


@dataclasses.dataclass
class OrderByAnnotation:
    allowed_fields: typing.FrozenSet[str]
    default_sort: typing.Optional['Sort'] = None
