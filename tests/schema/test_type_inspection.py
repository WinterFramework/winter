import datetime
import decimal
import uuid
from dataclasses import dataclass
from enum import Enum
from enum import IntEnum
from typing import Any
from typing import Generic
from typing import List
from typing import NewType
from typing import Optional
from typing import Set
from typing import TypeVar

import pytest
from drf_yasg import openapi

from winter.core.utils import TypeWrapper
from winter.data.pagination import Page
from winter_openapi import InspectorNotFound
from winter_openapi import TypeInfo
from winter_openapi import inspect_enum_class
from winter_openapi import inspect_type
from winter_openapi.type_inspection import TYPE_ANY_VALUE


class IntegerValueEnum(Enum):
    RED = 1
    GREEN = 2


TestType = NewType('TestType', int)


@dataclass
class NestedDataclass:
    nested_number: int


class Id(int):
    pass


@dataclass
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


class DataclassWrapper(TypeWrapper):
    pass


CustomPageItem = TypeVar('CustomPageItem')


@dataclass(frozen=True)
class CustomPage(Page, Generic[CustomPageItem]):
    extra: str


@pytest.mark.parametrize('type_hint, expected_type_info', [
    (TestType, TypeInfo(openapi.TYPE_INTEGER)),
    (Id, TypeInfo(openapi.TYPE_INTEGER)),
    (uuid.UUID, TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_UUID)),
    (bool, TypeInfo(openapi.TYPE_BOOLEAN)),
    (dict, TypeInfo(openapi.TYPE_OBJECT)),
    (float, TypeInfo(openapi.TYPE_NUMBER)),
    (decimal.Decimal, TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_DECIMAL)),
    (Optional[int], TypeInfo(openapi.TYPE_INTEGER, nullable=True)),
    (datetime.datetime, TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_DATETIME)),
    (datetime.date, TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_DATE)),
    (int, TypeInfo(openapi.TYPE_INTEGER)),
    (str, TypeInfo(openapi.TYPE_STRING)),
    (bytes, TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_BINARY)),
    (IntegerEnum, TypeInfo(openapi.TYPE_INTEGER, enum=[1, 2])),
    (IntegerValueEnum, TypeInfo(openapi.TYPE_INTEGER, enum=[1, 2])),
    (StringValueEnum, TypeInfo(openapi.TYPE_STRING, enum=['red', 'green'])),
    (MixedValueEnum, TypeInfo(openapi.TYPE_STRING, enum=[123, 'green'])),
    (List[IntegerValueEnum], TypeInfo(openapi.TYPE_ARRAY, child=TypeInfo(openapi.TYPE_INTEGER, enum=[1, 2]))),
    (List[StringValueEnum], TypeInfo(openapi.TYPE_ARRAY, child=TypeInfo(openapi.TYPE_STRING, enum=['red', 'green']))),
    (Any, TypeInfo(TYPE_ANY_VALUE)),
    (List, TypeInfo(openapi.TYPE_ARRAY, child=TypeInfo(TYPE_ANY_VALUE))),
    (List[Any], TypeInfo(openapi.TYPE_ARRAY, child=TypeInfo(TYPE_ANY_VALUE))),
    (Set[int], TypeInfo(openapi.TYPE_ARRAY, child=TypeInfo(openapi.TYPE_INTEGER))),
    (Dataclass(NestedDataclass(1)), TypeInfo(openapi.TYPE_OBJECT, properties={
        'nested': TypeInfo(openapi.TYPE_OBJECT, properties={
            'nested_number': TypeInfo(openapi.TYPE_INTEGER),
        }),
    })),
    (Page[NestedDataclass], TypeInfo(openapi.TYPE_OBJECT, properties={
        'meta': TypeInfo(openapi.TYPE_OBJECT, properties={
            'total_count': TypeInfo(openapi.TYPE_INTEGER),
            'limit': TypeInfo(openapi.TYPE_INTEGER, nullable=True),
            'offset': TypeInfo(openapi.TYPE_INTEGER, nullable=True),
            'previous': TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_URI, nullable=True),
            'next': TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_URI, nullable=True),
        }),
        'objects': TypeInfo(openapi.TYPE_ARRAY, child=TypeInfo(openapi.TYPE_OBJECT, properties={
            'nested_number': TypeInfo(openapi.TYPE_INTEGER),
        })),
    })),
    (CustomPage[int], TypeInfo(openapi.TYPE_OBJECT, properties={
        'meta': TypeInfo(openapi.TYPE_OBJECT, properties={
            'total_count': TypeInfo(openapi.TYPE_INTEGER),
            'limit': TypeInfo(openapi.TYPE_INTEGER, nullable=True),
            'offset': TypeInfo(openapi.TYPE_INTEGER, nullable=True),
            'previous': TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_URI, nullable=True),
            'next': TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_URI, nullable=True),
            'extra': TypeInfo(openapi.TYPE_STRING),
        }),
        'objects': TypeInfo(openapi.TYPE_ARRAY, child=TypeInfo(openapi.TYPE_INTEGER)),
    })),
    (DataclassWrapper[NestedDataclass], TypeInfo(openapi.TYPE_OBJECT, properties={
        'nested_number': TypeInfo(openapi.TYPE_INTEGER),
    })),
])
def test_inspect_type(type_hint, expected_type_info):
    # Act
    type_info = inspect_type(type_hint)

    # Assert
    assert type_info == expected_type_info, type_hint


def test_get_argument_type_info_with_non_registered_type():
    hint_class = object

    with pytest.raises(InspectorNotFound) as exception_info:
        # Act
        inspect_type(hint_class)
    assert exception_info.value.hint_cls == hint_class
    assert str(exception_info.value) == f'Unknown type: {hint_class}'


def test_get_openapi_schema():
    type_info = TypeInfo(openapi.TYPE_BOOLEAN)
    schema = openapi.Schema(type=openapi.TYPE_BOOLEAN)
    assert type_info.get_openapi_schema() == schema


@pytest.mark.parametrize(('first', 'second', 'is_same'), (
    (TypeInfo(openapi.TYPE_INTEGER), TypeInfo(openapi.TYPE_INTEGER), True),
    (TypeInfo(openapi.TYPE_INTEGER), TypeInfo(openapi.TYPE_NUMBER), False),
    (TypeInfo(openapi.TYPE_INTEGER), None, False),
))
def test_compare_type_info(first, second, is_same):
    assert (first == second) is is_same


@pytest.mark.parametrize(('enum_cls', 'expected_value'), (
    (IntegerValueEnum, {
        'enum': [1, 2],
        'type': 'integer',
    }),
    (StringValueEnum, {
        'enum': ['red', 'green'],
        'type': 'string',
    }),
))
def test_inspect_enum_class(enum_cls, expected_value):
    assert inspect_enum_class(enum_cls) == expected_value


@pytest.mark.parametrize(('type_info', 'expected_data'), (
    (
        TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_URI, nullable=True),
        {'format': 'uri', 'type': 'string', 'x-nullable': True},
    ),
    (
        TypeInfo(openapi.TYPE_INTEGER, enum=[1, 2]),
        {'enum': [1, 2], 'type': 'integer'},
    ),
    (
        TypeInfo(openapi.TYPE_OBJECT, properties={'nested_number': TypeInfo(openapi.TYPE_INTEGER)}),
        {'properties': {'nested_number': {'type': 'integer'}}, 'type': 'object'},
    ),
    (
        TypeInfo(openapi.TYPE_ARRAY, child=TypeInfo(openapi.TYPE_INTEGER)),
        {'items': {'type': 'integer'}, 'type': 'array'},
    ),
))
def test_as_dict_in_type_info(type_info, expected_data):
    assert type_info.as_dict() == expected_data
