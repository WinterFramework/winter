import enum
import uuid

import winter


class OneTwoEnum(enum.Enum):
    ONE = 'one'
    TWO = 'two'


class OneTwoEnumWithInt(enum.Enum):
    ONE = 1
    TWO = 2

    @classmethod
    def _missing_(cls, value):  # This is need because of needing of instancing from string
        try:
            value = int(value)
        except ValueError:
            super()._missing_(cls, value)
        else:
            return cls(value)


@winter.controller
@winter.route('controller_with_path_parameters/{param1}/')
class ControllerWithPathParameters:

    @winter.query_parameter('param6')
    @winter.route_get('{param2}/{param3}/{param4}/{param5}/')
    def test(
            self,
            param1: str,
            param2: int,
            param3: OneTwoEnum,
            param4: uuid.UUID,
            param5: OneTwoEnumWithInt,
            param6: str,
    ) -> str:
        return 'Hello, sir!'
