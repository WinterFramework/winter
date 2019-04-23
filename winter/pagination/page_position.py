import typing

import dataclasses


@dataclasses.dataclass(frozen=True)
class PagePosition:
    limit: typing.Optional[int] = None
    offset: typing.Optional[int] = None

    def __post_init__(self):
        if self.limit == 0:
            object.__setattr__(self, 'limit', None)
