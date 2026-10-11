from typing import Optional

import dataclasses

from .sort import Sort


@dataclasses.dataclass(frozen=True)
class PagePosition:
    limit: Optional[int] = None
    offset: Optional[int] = None
    sort: Optional[Sort] = None

    def __post_init__(self):
        if self.limit == 0:
            object.__setattr__(self, 'limit', None)
