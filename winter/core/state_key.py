import typing

import dataclasses


@dataclasses.dataclass(frozen=True)
class StateKey:
    key: typing.Hashable
    many: bool = False
