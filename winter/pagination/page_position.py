import typing

import dataclasses


@dataclasses.dataclass(frozen=True)
class PagePosition:
    limit: typing.Optional[int] = None
    offset: typing.Optional[int] = None
