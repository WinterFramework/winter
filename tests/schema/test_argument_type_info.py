from enum import Enum
from enum import IntEnum
from typing import List

import pytest
from drf_yasg import openapi

from winter.core import ComponentMethod
from winter.schema.generation import get_argument_info


class IntegerValueEnum(Enum):
    RED = 1
    GREEN = 2


class StringValueEnum(Enum):
    RED = 'red'
    GREEN = 'green'


class MixedValueEnum(Enum):
    RED = 123
    GREEN = 'green'


class IntegerEnum(IntEnum):
    RED = 1
    GREEN = 2


@pytest.mark.parametrize('type_hint, expected_type_info', [
    (object, {'type': 'string', 'description': '(Note: parameter type can be wrong)', 'default': None}),
    (int, {'type': openapi.TYPE_INTEGER, 'description': '', 'default': None}),
    (str, {'type': openapi.TYPE_STRING, 'description': '', 'default': None}),
    (IntegerEnum, {'type': openapi.TYPE_INTEGER, 'enum': [1, 2], 'description': '', 'default': None}),
    (IntegerValueEnum, {'type': openapi.TYPE_INTEGER, 'enum': [1, 2], 'description': '', 'default': None}),
    (StringValueEnum, {'type': openapi.TYPE_STRING, 'enum': ['red', 'green'], 'description': '', 'default': None}),
    (MixedValueEnum, {'type': openapi.TYPE_STRING, 'enum': [123, 'green'], 'description': '', 'default': None}),
    (List[IntegerValueEnum], {
        'type': openapi.TYPE_ARRAY, 'items': {'type': openapi.TYPE_INTEGER, 'enum': [1, 2]}, 'description': '',
        'default': None,
    }),
    (List[StringValueEnum], {
        'type': openapi.TYPE_ARRAY, 'items': {'type': openapi.TYPE_STRING, 'enum': ['red', 'green']},
        'description': '',
        'default': None,
    }),
])
def test_get_argument_type_info(type_hint, expected_type_info):
    def func(arg_1: type_hint):
        return arg_1

    argument = ComponentMethod(func).get_argument('arg_1')

    # Act
    type_info_data = get_argument_info(argument)

    # Assert
    assert type_info_data == expected_type_info
