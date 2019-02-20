import typing

import dataclasses


@dataclasses.dataclass(frozen=True)
class MetadataKey:
    key: typing.Hashable
    many: bool = False
