import typing

import dataclasses

from ..page_position import PagePosition

T = typing.TypeVar('T')


@dataclasses.dataclass(frozen=True)
class Page(typing.Generic[T]):
    total_count: int
    items: typing.Iterable[T]
    position: PagePosition

    def __iter__(self) -> typing.Iterator[T]:
        return iter(self.items)
