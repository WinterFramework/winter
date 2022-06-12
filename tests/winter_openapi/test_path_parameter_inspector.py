from enum import Enum
from enum import IntEnum
from typing import List

import pytest
from drf_yasg import openapi

import winter
from winter.web.routing import get_route
from winter_openapi import PathParametersInspector


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


@pytest.mark.parametrize('type_hint, expected_parameter_properties', [
    (object, {'type': openapi.TYPE_STRING, 'description': 'winter_openapi has failed to inspect the parameter'}),
    (int, {'type': openapi.TYPE_INTEGER, 'description': 'docstr'}),
    (str, {'type': openapi.TYPE_STRING, 'description': 'docstr'}),
    (IntegerEnum, {'type': openapi.TYPE_INTEGER, 'enum': [1, 2], 'description': 'docstr'}),
    (IntegerValueEnum, {'type': openapi.TYPE_INTEGER, 'enum': [1, 2], 'description': 'docstr'}),
    (StringValueEnum, {'type': openapi.TYPE_STRING, 'enum': ['red', 'green'], 'description': 'docstr'}),
    (MixedValueEnum, {'type': openapi.TYPE_STRING, 'enum': [123, 'green'], 'description': 'docstr'}),
    (List[IntegerValueEnum], {
        'type': openapi.TYPE_ARRAY,
        'items': {'type': openapi.TYPE_INTEGER, 'enum': [1, 2]},
        'description': 'docstr',
    }),
    (List[StringValueEnum], {
        'type': openapi.TYPE_ARRAY,
        'items': {'type': openapi.TYPE_STRING, 'enum': ['red', 'green']},
        'description': 'docstr',
    }),
])
def test_path_parameter_inspector(type_hint, expected_parameter_properties):
    class _TestController:
        @winter.route_post('{param}/{not_in_method}/{?query_parameter}')
        def simple_method(
            self,
            param: type_hint,
            query_parameter: int,
        ):  # pragma: no cover
            """
            :param param: docstr
            :param query_parameter: Invalid doc
            """
            pass

    inspector = PathParametersInspector()
    route = get_route(_TestController.simple_method)
    expected_parameter = openapi.Parameter(
        name='param',
        in_=openapi.IN_PATH,
        required=True,
        default=None,
        **expected_parameter_properties,
    )

    # Act
    parameters = inspector.inspect_parameters(route)

    # Assert
    assert parameters == [expected_parameter]

