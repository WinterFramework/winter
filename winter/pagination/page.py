from typing import Generic
from typing import Iterable
from typing import Iterator
from typing import TypeVar

import dataclasses

from .page_position import PagePosition

T = TypeVar('T')


@dataclasses.dataclass(frozen=True)
class Page(Generic[T]):
    total_count: int
    items: Iterable[T]
    position: PagePosition

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)
