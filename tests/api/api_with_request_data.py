import enum
from typing import List
from typing import Optional

import dataclasses

import winter


class Status(enum.Enum):
    ACTIVE = 'active'
    SUPER_ACTIVE = 'super_active'


@dataclasses.dataclass
class Data:
    id: int
    name: str
    is_god: bool
    optional_status: Optional[Status]
    status: Status
    items: List[int]
    optional_items: Optional[List[int]]
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
