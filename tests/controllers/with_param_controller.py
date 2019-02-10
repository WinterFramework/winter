import uuid

import winter
from ..enums import OneTwoEnum


@winter.controller
@winter.route('with-param/')
class ControllerWithParam:

    @winter.route_get('{param}/')
    def with_enum_param(self, param: OneTwoEnum):
        return {
            'type': 'enum',
            'param': param,
        }

    @winter.route_get('{param}/')
    def with_int_param(self, param: int):
        return {
            'type': 'int',
            'param': param,
        }

    @winter.route_get('{param}/')
    def with_uuid_param(self, param: uuid.UUID) -> uuid.UUID:
        return {
            'type': 'uuid',
            'param': param,
        }

    @winter.route_get('{param}/')
    def with_str_param(self, param: str):
        return {
            'type': 'str',
            'param': param,
        }
