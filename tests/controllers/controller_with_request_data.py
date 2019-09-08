import enum
import typing

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
    optional_status: typing.Optional[Status]
    status: Status
    items: typing.List[int]
    optional_items: typing.Optional[typing.List[int]]
    with_default: int = 5


@winter.controller
@winter.route('with-request-data/')
class ControllerWithRequestData:

    @winter.request_body('data')
    @winter.route_post('{?query}')
    def method(self, query: typing.Optional[str], data: Data) -> Data:
        return data

    @winter.request_body('data')
    @winter.route_post('many/')
    def many_method(self, data: typing.List[Data]) -> Data:
        return data
