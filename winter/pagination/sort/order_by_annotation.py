import typing

import dataclasses


@dataclasses.dataclass
class OrderByAnnotation:
    allowed_fields: typing.FrozenSet[str]
    default: typing.Optional[str]
