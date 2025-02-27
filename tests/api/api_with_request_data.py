import enum
from typing import List
from typing import NotRequired
from typing import Optional

import dataclasses
from typing import Required
from typing import TypeAlias
from typing import TypedDict

import winter


class Status(enum.Enum):
    ACTIVE = 'active'
    SUPER_ACTIVE = 'super_active'


ItemsTypeAlias: TypeAlias = list[int]


class TypedDictExample(TypedDict):
    field: str
    required_field: Required[int]
    optional_field: NotRequired[int]


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
    typed_dict: TypedDictExample
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
