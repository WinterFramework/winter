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
        return cls(int(value))


@winter.route('with-path-parameters/{param1}/')
class APIWithPathParameters:
    @winter.route_get('{param2}/{param3}/{param4}/{param5}/{?param6}')
    def test(
        self,
        param1: str,
        param2: int,
        param3: OneTwoEnum,
        param4: uuid.UUID,
        param5: OneTwoEnumWithInt,
        param6: str,
    ) -> str:  # pragma: no cover
        pass
