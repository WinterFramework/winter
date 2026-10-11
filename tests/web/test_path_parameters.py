import uuid

import pytest

from tests.utils import get_request
from tests.api.api_with_path_parameters import APIWithPathParameters
from tests.api.api_with_path_parameters import OneTwoEnum
from tests.api.api_with_path_parameters import OneTwoEnumWithInt
from winter.components import Component
from winter.web.argument_resolver import ArgumentNotSupported
from winter.web.path_parameters_argument_resolver import PathParametersArgumentResolver

uuid_ = uuid.uuid4()


path_parameters = {'param1': '123', 'param2': '456', 'param3': 'one', 'param4': str(uuid_), 'param5': '2'}


@pytest.mark.parametrize(
    'arg_name, expected_value', [
        ('param1', '123'),
        ('param2', 456),
        ('param3', OneTwoEnum.ONE),
        ('param4', uuid_),
        ('param5', OneTwoEnumWithInt.TWO),
    ],
)
def test_resolve_path_parameter(arg_name, expected_value):
    component = Component.get_by_cls(APIWithPathParameters)
    argument = component.get_method('test').get_argument(arg_name)
    resolver = PathParametersArgumentResolver()
    request = get_request(path_parameters=path_parameters)

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
    request = get_request(path_parameters=path_parameters)

    with pytest.raises(ArgumentNotSupported) as exception:
        resolver.resolve_argument(argument, request, {})

    assert str(exception.value) == 'Unable to resolve argument param6: str'
