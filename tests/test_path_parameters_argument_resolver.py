import uuid

import pytest
from mock import Mock
from rest_framework.request import Request

from tests.controllers.controller_with_path_parameters import ControllerWithPathParameters
from tests.controllers.controller_with_path_parameters import OneTwoEnum
from tests.controllers.controller_with_path_parameters import OneTwoEnumWithInt
from winter.argument_resolver import ArgumentNotSupported
from winter.controller import get_component
from winter.core import Component
from winter.path_parameters_argument_resolver import PathParametersArgumentResolver

uuid_ = uuid.uuid4()


@pytest.mark.parametrize('path, arg_name, expected_value', [
    (f'/controller_with_path_parameters/123/456/one/{uuid_}/2/', 'param1', '123'),
    (f'/controller_with_path_parameters/123/456/one/{uuid_}/2/', 'param2', 456),
    (f'/controller_with_path_parameters/123/456/one/{uuid_}/2/', 'param3', OneTwoEnum.ONE),
    (f'/controller_with_path_parameters/123/456/one/{uuid_}/2/', 'param4', uuid_),
    (f'/controller_with_path_parameters/123/456/one/{uuid_}/2/', 'param5', OneTwoEnumWithInt.TWO),
])
def test_resolve_path_parameter(path, arg_name, expected_value):
    component = Component.get_by_cls(ControllerWithPathParameters)
    argument = component.get_method('test').get_argument(arg_name)
    resolver = PathParametersArgumentResolver()
    http_request = Mock(spec=Request)
    http_request.path_info = path

    # Act
    result = resolver.resolve_argument(argument, http_request)

    # Assert
    assert result == expected_value


@pytest.mark.parametrize('controller_class, method_name, arg_name, expected_value', [
    (ControllerWithPathParameters, 'test', 'param1', True),
    (ControllerWithPathParameters, 'test', 'param2', True),
    (ControllerWithPathParameters, 'test', 'param6', False),
])
def test_is_supported_path_parameter(controller_class, method_name, arg_name, expected_value):
    component = get_component(controller_class)
    argument = component.get_method(method_name).get_argument(arg_name)
    resolver = PathParametersArgumentResolver()

    # Act
    is_supported = resolver.is_supported(argument)
    second_is_supported = resolver.is_supported(argument)

    # Assert
    assert is_supported == second_is_supported == expected_value


def test_with_raises_argument_not_supported():
    component = get_component(ControllerWithPathParameters)
    argument = component.get_method('test').get_argument('param6')
    resolver = PathParametersArgumentResolver()
    http_request = Mock(spec=Request)
    http_request.path_info = f'/controller_with_path_parameters/123/456/one/{uuid_}/2/'

    with pytest.raises(ArgumentNotSupported) as exception:
        resolver.resolve_argument(argument, http_request)

    assert str(exception.value) == 'Unable to resolve argument param6: str'
