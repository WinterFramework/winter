import typing

import dataclasses

from ...data.pagination import Sort


@dataclasses.dataclass
class OrderByAnnotation:
    allowed_fields: typing.FrozenSet[str]
    default_sort: typing.Optional[Sort] = None
