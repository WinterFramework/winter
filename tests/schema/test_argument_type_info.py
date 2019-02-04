import datetime
import decimal
import typing
import uuid
from enum import Enum
from enum import IntEnum
from typing import List

import dataclasses
import pytest
from drf_yasg import openapi

from winter.controller import ControllerMethod
from winter.schema.generation import get_argument_type_info
from winter.schema.type_hint import TYPE_NONE


class IntegerValueEnum(Enum):
    RED = 1
    GREEN = 2


@dataclasses.dataclass
class NestedDataclass:
    nested_number: int


class Id(int):
    pass


@dataclasses.dataclass
class Dataclass:
    nested: NestedDataclass


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
    (Id, {
        'type': openapi.TYPE_INTEGER
    }),
    (None, {
        'type': TYPE_NONE,
    }),
    (uuid.UUID, {
        'type': openapi.TYPE_STRING,
        'format': openapi.FORMAT_UUID,
    }),
    (bool, {
        'type': openapi.TYPE_BOOLEAN,
    }),
    (dict, {
        'type': openapi.TYPE_OBJECT,
    }),
    (float, {
        'type': openapi.TYPE_NUMBER,
    }),
    (decimal.Decimal, {
        'type': openapi.TYPE_STRING,
        'format': openapi.FORMAT_DECIMAL,
    }),
    (typing.Optional[int], {
        'type': openapi.TYPE_INTEGER,
        'x-nullable': True
    }
    ),
    (datetime.date, {
        'type': openapi.TYPE_STRING,
        'format': openapi.FORMAT_DATE,
    }),
    (datetime.datetime, {
        'type': openapi.TYPE_STRING,
        'format': openapi.FORMAT_DATETIME,
    }),

    (int, {
        'type': openapi.TYPE_INTEGER
    }),
    (str, {
        'type': openapi.TYPE_STRING
    }),
    (IntegerEnum, {
        'type': openapi.TYPE_INTEGER,
        'enum': [1, 2]
    }),
    (IntegerValueEnum, {
        'type': openapi.TYPE_INTEGER,
        'enum': [1, 2]
    }),
    (StringValueEnum, {
        'type': openapi.TYPE_STRING,
        'enum': ['red', 'green']
    }),
    (MixedValueEnum, {
        'type': openapi.TYPE_STRING,
        'enum': [123, 'green']
    }),
    (List[IntegerValueEnum], {
        'type': openapi.TYPE_ARRAY,
        'items': {
            'type': openapi.TYPE_INTEGER,
            'enum': [1, 2]
        }
    }),
    (List[StringValueEnum], {
        'type': openapi.TYPE_ARRAY,
        'items': {
            'type': openapi.TYPE_STRING,
            'enum': ['red', 'green']
        }
    }),
    (Dataclass(NestedDataclass(1)), {
        'type': 'object',
        'properties': {
            'nested': {
                'type': 'object',
                'properties': {
                    'nested_number': {
                        'type': 'integer'
                    }
                }
            }
        }
    })
])
def test_get_argument_type_info(type_hint, expected_type_info):
    def func(arg_1: type_hint):
        return arg_1

    argument = ControllerMethod(func, '/', 'GET').get_argument('arg_1')

    # Act
    type_info = get_argument_type_info(argument)

    # Assert
    assert type_info == expected_type_info


def test_get_argument_type_info_with_non_registered_type():
    hint_class = object
    def func(arg_1: hint_class):
        return arg_1

    argument = ControllerMethod(func, '/', 'GET').get_argument('arg_1')

    with pytest.raises(ValueError) as exception_info:
        # Act
        type_info = get_argument_type_info(argument)
    assert exception_info.value.args[0] == f'Unknown type: {hint_class}'