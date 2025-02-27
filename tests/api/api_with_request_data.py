import enum
from typing import List
from typing import Optional

import dataclasses
from typing import TypeAlias

import winter


class Status(enum.Enum):
    ACTIVE = 'active'
    SUPER_ACTIVE = 'super_active'

ItemsTypeAlias: TypeAlias = list[int]


@dataclasses.dataclass
class Data:
    id: int
    name: str
    is_god: bool
    optional_status: Optional[Status]
    optional_status_new_typing_style: Status | None
    status: Status
    items: List[int]
    items_alias: ItemsTypeAlias
    optional_items: Optional[List[int]]
    optional_items_new_typing_style: list[int] | None
    with_default: int = 5


class APIWithRequestData:

    @winter.request_body('data')
    @winter.route_post('with-request-data/{?query}')
    def method(self, query: Optional[str], data: Data) -> Data:
        return data

    @winter.request_body('data')
    @winter.route_post('with-request-data/many/')
    def many_method(self, data: List[Data]) -> List[Data]:
        return data
