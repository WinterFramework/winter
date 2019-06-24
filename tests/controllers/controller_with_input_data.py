import enum

import pydantic

import winter


class Status(enum.Enum):
    ACTIVE = 'active'
    SUPER_ACTIVE = 'super_active'


@pydantic.dataclasses.dataclass
class InputData:
    id: int
    name: str
    is_god: bool
    status: Status


@winter.controller
@winter.route('with-input-data/')
class ControllerWithInputData:

    @winter.input_data(InputData, to='data')
    @winter.route_post()
    def method(self, data: InputData) -> InputData:
        return data
