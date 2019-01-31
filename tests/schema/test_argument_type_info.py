from enum import Enum
from typing import List

import pytest
from drf_yasg import openapi

from winter.controller import ControllerMethod

from winter.schema.generation import get_argument_type_info


class IntegersEnum(Enum):
    RED = 1
    GREEN = 2


class StringsEnum(Enum):
    RED = 'red'
    GREEN = 'green'


class MixedEnum(Enum):
    RED = 123
    GREEN = 'green'


@pytest.mark.parametrize('type_hint, expected_type_info', [
    (int, {'type': openapi.TYPE_INTEGER, 'format': None}),
    (str, {'type': openapi.TYPE_STRING, 'format': None}),
    (IntegersEnum, {'type': openapi.TYPE_INTEGER, 'enum': [1, 2]}),
    (StringsEnum, {'type': openapi.TYPE_STRING, 'enum': ['red', 'green']}),
    (MixedEnum, {'type': openapi.TYPE_STRING, 'enum': [123, 'green']}),
    (List[IntegersEnum], {'type': openapi.TYPE_ARRAY, 'items': {'type': openapi.TYPE_INTEGER, 'enum': [1, 2]}}),
    (List[StringsEnum], {'type': openapi.TYPE_ARRAY, 'items': {'type': openapi.TYPE_STRING, 'enum': ['red', 'green']}}),
])
def test_get_argument_type_info(type_hint, expected_type_info):
    def func(arg_1: type_hint):
        return arg_1

    argument = ControllerMethod(func, '/', 'GET').get_argument('arg_1')

    # Act
    type_info = get_argument_type_info(argument)

    # Assert
    assert type_info == expected_type_info
