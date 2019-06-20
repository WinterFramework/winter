import typing

import dataclasses

from .sort import Sort


@dataclasses.dataclass(frozen=True)
class PagePosition:
    limit: typing.Optional[int] = None
    offset: typing.Optional[int] = None
    sort: typing.Optional[Sort] = None

    def __post_init__(self):
        if self.limit == 0:
            object.__setattr__(self, 'limit', None)
