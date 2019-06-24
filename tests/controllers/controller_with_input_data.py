import enum
import typing

import dataclasses

import winter


class Status(enum.Enum):
    ACTIVE = 'active'
    SUPER_ACTIVE = 'super_active'


@dataclasses.dataclass
class InputData:
    id: int
    name: str
    is_god: bool
    optional_status: typing.Optional[Status]
    status: Status
    items: typing.List[int]
    optional_items: typing.Optional[typing.List[int]]
    with_default: int = 5


@winter.controller
@winter.route('with-input-data/')
class ControllerWithInputData:

    @winter.input_data(InputData, to='data')
    @winter.route_post()
    def method(self, data: InputData) -> InputData:
        return data
