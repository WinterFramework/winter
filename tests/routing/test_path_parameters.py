import uuid

import pytest
from django.http import HttpRequest
from mock import Mock

from tests.api.api_with_path_parameters import APIWithPathParameters
from tests.api.api_with_path_parameters import OneTwoEnum
from tests.api.api_with_path_parameters import OneTwoEnumWithInt
from winter.core import Component
from winter.web.argument_resolver import ArgumentNotSupported
from winter.web.path_parameters_argument_resolver import PathParametersArgumentResolver

uuid_ = uuid.uuid4()


@pytest.mark.parametrize(
    'path, arg_name, expected_value', [
        (f'/with-path-parameters/123/456/one/{uuid_}/2/', 'param1', '123'),
        (f'/with-path-parameters/123/456/one/{uuid_}/2/', 'param2', 456),
        (f'/with-path-parameters/123/456/one/{uuid_}/2/', 'param3', OneTwoEnum.ONE),
        (f'/with-path-parameters/123/456/one/{uuid_}/2/', 'param4', uuid_),
        (f'/with-path-parameters/123/456/one/{uuid_}/2/', 'param5', OneTwoEnumWithInt.TWO),
    ],
)
def test_resolve_path_parameter(path, arg_name, expected_value):
    component = Component.get_by_cls(APIWithPathParameters)
    argument = component.get_method('test').get_argument(arg_name)
    resolver = PathParametersArgumentResolver()
    request = Mock(spec=HttpRequest)
    request.path_info = path

    # Act
    result = resolver.resolve_argument(argument, request, {})

    # Assert
    assert result == expected_value


@pytest.mark.parametrize(
    'api_class, method_name, arg_name, expected_value', [
        (APIWithPathParameters, 'test', 'param1', True),
        (APIWithPathParameters, 'test', 'param2', True),
        (APIWithPathParameters, 'test', 'param6', False),
    ],
)
def test_is_supported_path_parameter(api_class, method_name, arg_name, expected_value):
    component = Component.get_by_cls(api_class)
    argument = component.get_method(method_name).get_argument(arg_name)
    resolver = PathParametersArgumentResolver()

    # Act
    is_supported = resolver.is_supported(argument)
    second_is_supported = resolver.is_supported(argument)

    # Assert
    assert is_supported == expected_value
    assert second_is_supported == expected_value


def test_with_raises_argument_not_supported():
    component = Component.get_by_cls(APIWithPathParameters)
    argument = component.get_method('test').get_argument('param6')
    resolver = PathParametersArgumentResolver()
    request = Mock(spec=Request)
    request.path_info = f'/with-path-parameters/123/456/one/{uuid_}/2/'

    with pytest.raises(ArgumentNotSupported) as exception:
        resolver.resolve_argument(argument, request, {})

    assert str(exception.value) == 'Unable to resolve argument param6: str'
