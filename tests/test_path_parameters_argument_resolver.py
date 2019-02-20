import pytest
from mock import Mock
from rest_framework.request import Request

from tests.controllers.controller_with_path_parameters import ControllerWithPathParameters
from winter.controller import get_controller_component
from winter.path_parameters_argument_resolver import PathParametersArgumentResolver


@pytest.mark.parametrize('path, arg_name, expected_value', [
    ('/controller_with_path_parameters/123/456/', 'param1', '123'),
    ('/controller_with_path_parameters/123/456/', 'param2', 456),
])
def test_resolve_path_parameter(path, arg_name, expected_value):
    controller_component = get_controller_component(ControllerWithPathParameters)
    argument = controller_component.get_method('test').get_argument(arg_name)
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
    (ControllerWithPathParameters, 'test', 'param3', False),
])
def test_is_supported_path_parameter(controller_class, method_name, arg_name, expected_value):
    controller_component = get_controller_component(controller_class)
    argument = controller_component.get_method(method_name).get_argument(arg_name)
    resolver = PathParametersArgumentResolver()

    # Act
    result = resolver.is_supported(argument)

    # Assert
    assert result == expected_value
