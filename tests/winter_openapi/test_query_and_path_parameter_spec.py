from enum import Enum
from enum import IntEnum
from typing import List

import pytest

import winter
from winter.web.routing import get_route
from winter_openapi import generate_openapi


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


param_with_diff_types = [
    (object, {'schema': {'type': 'string'}, 'description': 'winter_openapi has failed to inspect the parameter'}),
    (int, {'schema': {'format': 'int32', 'type': 'integer'}}),
    (str, {'schema': {'type': 'string'}}),
    (IntegerEnum, {'schema': {'enum': [1, 2], 'format': 'int32', 'type': 'integer'}}),
    (IntegerValueEnum, {'schema': {'enum': [1, 2], 'format': 'int32', 'type': 'integer'}}),
    (StringValueEnum, {'schema': {'enum': ['red', 'green'], 'type': 'string'}}),
    (MixedValueEnum, {'schema': {'enum': [123, 'green'], 'type': 'string'}}),
    (List[IntegerValueEnum], {
        'schema': {'items': {'enum': [1, 2], 'format': 'int32', 'type': 'integer'}, 'type': 'array'}
    }),
    (List[StringValueEnum], {
        'schema': {'items': {'enum': ['red', 'green'], 'type': 'string'}, 'type': 'array'}
    }),
]


@pytest.mark.parametrize('type_hint, expected_parameter_properties', param_with_diff_types)
def test_query_parameter_inspector(type_hint, expected_parameter_properties):
    class _TestAPI:
        @winter.route_get('/resource/{?query_param}')
        @winter.map_query_parameter('mapped_query_param', to='invalid_query_param')
        def simple_method(
            self,
            query_param: type_hint,
        ):  # pragma: no cover
            """
            :param query_param: docstr
            """
            pass

    expected_parameter = {
        'name': 'query_param',
        'in': 'query',
        'required': True,
        'allowEmptyValue': False,
        'allowReserved': False,
        'deprecated': False,
        'explode': False,
        'description': 'docstr',
        **expected_parameter_properties,
    }
    route = get_route(_TestAPI.simple_method)
    # Act
    result = generate_openapi(title='title', version='1.0.0', routes=[route])

    # Assert
    parameters = result["paths"]["/resource/"]["get"]["parameters"]
    assert parameters == [expected_parameter]


@pytest.mark.parametrize('type_hint, expected_parameter_properties', param_with_diff_types)
def test_query_parameter_inspector_with_explode(type_hint, expected_parameter_properties):
    class _TestAPI:
        @winter.route_get('/resource/{?query_param*}')
        @winter.map_query_parameter('mapped_query_param', to='invalid_query_param')
        def simple_method(
            self,
            query_param: type_hint,
        ):  # pragma: no cover
            """
            :param query_param: docstr
            """
            pass

    expected_parameter = {
        'name': 'query_param',
        'in': 'query',
        'required': True,
        'allowEmptyValue': False,
        'allowReserved': False,
        'deprecated': False,
        'explode': True,
        'description': 'docstr',
        **expected_parameter_properties,
    }
    route = get_route(_TestAPI.simple_method)
    # Act
    result = generate_openapi(title='title', version='1.0.0', routes=[route])

    # Assert
    parameters = result["paths"]["/resource/"]["get"]["parameters"]
    assert parameters == [expected_parameter]


@pytest.mark.parametrize('type_hint, expected_parameter_properties', param_with_diff_types)
def test_path_parameter_different_types(type_hint, expected_parameter_properties):
    class _TestAPI:
        @winter.route_post('{param}/{not_in_method}/')
        def simple_method_with_path_param(
            self,
            param: type_hint,
        ):  # pragma: no cover
            """
            :param param: docstr
            """
            pass

    route = get_route(_TestAPI.simple_method_with_path_param)
    expected_parameter = {
        'name': 'param',
        'in': 'path',
        'required': True,
        'allowEmptyValue': False,
        'allowReserved': False,
        'deprecated': False,
        'explode': False,
        'description': 'docstr',
        **expected_parameter_properties,
    }

    # Act
    result = generate_openapi(title='title', version='1.0.0', routes=[route])

    # Assert
    parameters = result["paths"]["{param}/{not_in_method}/"]["post"]["parameters"]
    assert parameters == [expected_parameter]


def test_query_parameter_without_python_argument():
    class _TestAPI:
        @winter.route_post('{?test}')
        def api_method(
            self,
        ):  # pragma: no cover
            """
            :param param: docstr
            """
            pass

    route = get_route(_TestAPI.api_method)

    # Act
    with pytest.raises(Exception) as exc_info:
        generate_openapi(title='title', version='1.0.0', routes=[route])

    # Assert
    assert str(exc_info.value) == 'Argument "test" not found in _TestAPI.api_method, but listed in query parameters'
