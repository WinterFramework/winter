import itertools

import pytest
from mock import Mock

from winter import GenericArgumentResolver, ArgumentsResolver
from winter.argument_resolver import ArgumentNotSupported
from winter.controller import ControllerMethodArgument, ControllerMethod


@pytest.mark.parametrize('arg_name, arg_type, resolver_arg_name, resolver_arg_type, expected_supported', [
    ('a', int, 'a', int, True),
    ('a', int, 'b', int, False),
    ('a', int, 'a', str, False),
    ('a', int, 'b', str, False),
])
def test_generic_argument_resolver_is_supported(arg_name, arg_type, resolver_arg_name, resolver_arg_type, expected_supported):
    resolve_argument_mock = Mock()
    generic_argument_resolver = GenericArgumentResolver(resolver_arg_name, resolver_arg_type, resolve_argument_mock)
    argument = ControllerMethodArgument(Mock(), arg_name, arg_type)

    # Act
    is_supported = generic_argument_resolver.is_supported(argument)

    # Assert
    assert is_supported is expected_supported
    resolve_argument_mock.assert_not_called()


def test_generic_argument_resolver_resolve_argument():
    arg_name = 'a'
    arg_type = int
    expected_result = 1
    argument = ControllerMethodArgument(Mock(), arg_name, arg_type)
    resolve_argument_mock = Mock()
    resolve_argument_mock.return_value = expected_result
    generic_argument_resolver = GenericArgumentResolver(arg_name, arg_type, resolve_argument_mock)
    http_request = object()

    # Act
    result = generic_argument_resolver.resolve_argument(argument, http_request)

    # Assert
    resolve_argument_mock.assert_called_once_with(http_request)
    assert result == expected_result


def test_resolve_arguments_returns_empty_dict_for_empty_arguments():
    def func():
        pass

    expected_resolved_arguments = {}
    controller_method = ControllerMethod(func, '', '')
    arguments_resolver = ArgumentsResolver()

    # Act
    resolved_arguments = arguments_resolver.resolve_arguments(controller_method, http_request=Mock(), path_variables={})

    # Assert
    assert resolved_arguments == expected_resolved_arguments


def test_resolve_arguments_resolves_argument_with_the_first_resolver():
    def func(a: int):
        pass

    expected_resolved_value = 1
    expected_resolved_arguments = {'a': expected_resolved_value}
    controller_method = ControllerMethod(func, '', '')
    arguments_resolver = ArgumentsResolver()
    resolver = Mock()
    resolver.is_supported.return_value = True
    resolver.resolve_argument.return_value = expected_resolved_value
    arguments_resolver.add_argument_resolver(resolver)

    # Act
    resolved_arguments = arguments_resolver.resolve_arguments(controller_method, http_request=Mock(), path_variables={})

    # Assert
    assert resolved_arguments == expected_resolved_arguments


def test_resolve_arguments_resolves_argument_with_the_second_resolver():
    def func(a: int):
        pass

    expected_resolved_value = 1
    expected_resolved_arguments = {'a': expected_resolved_value}
    controller_method = ControllerMethod(func, '', '')
    arguments_resolver = ArgumentsResolver()
    resolver1 = Mock()
    resolver1.is_supported.return_value = False
    arguments_resolver.add_argument_resolver(resolver1)
    resolver2 = Mock()
    resolver2.is_supported.return_value = True
    resolver2.resolve_argument.return_value = expected_resolved_value
    arguments_resolver.add_argument_resolver(resolver2)

    # Act
    resolved_arguments = arguments_resolver.resolve_arguments(controller_method, http_request=Mock(), path_variables={})

    # Assert
    assert resolved_arguments == expected_resolved_arguments


def test_resolve_arguments_resolves_argument_with_the_path_variable():
    def func(a: int):
        pass

    arg_name = 'a'
    expected_resolved_value = 1
    expected_resolved_arguments = {arg_name: expected_resolved_value}
    controller_method = ControllerMethod(func, '', '')
    path_variables = {arg_name: str(expected_resolved_value)}
    arguments_resolver = ArgumentsResolver()

    # Act
    resolved_arguments = arguments_resolver.resolve_arguments(
        controller_method,
        http_request=Mock(),
        path_variables=path_variables,
    )

    # Assert
    assert resolved_arguments == expected_resolved_arguments


def test_resolve_arguments_fails():
    def func(a: int):
        pass

    arg_name = 'a'
    controller_method = ControllerMethod(func, '', '')
    arguments_resolver = ArgumentsResolver()

    # Assert
    with pytest.raises(ArgumentNotSupported, match=f'Unable to resolve argument {arg_name}: int'):
        # Act
        arguments_resolver.resolve_arguments(controller_method, http_request=Mock(), path_variables={})


@pytest.mark.parametrize('resolver1_supported, resolver2_supported', itertools.product([False, True], repeat=2))
def test_arguments_resolver_is_supported_true(resolver1_supported, resolver2_supported):
    arguments_resolver = ArgumentsResolver()
    resolver1 = Mock(spec_set=GenericArgumentResolver)
    resolver1.is_supported.return_value = resolver1_supported
    arguments_resolver.add_argument_resolver(resolver1)
    resolver2 = Mock(spec_set=GenericArgumentResolver)
    resolver2.is_supported.return_value = resolver2_supported
    arguments_resolver.add_argument_resolver(resolver2)
    argument = object()

    # Act
    is_supported = arguments_resolver.is_supported(argument)

    # Assert
    assert is_supported is (resolver1_supported or resolver2_supported)
    resolver1.is_supported.assert_called_once_with(argument)
    assert resolver2.is_supported.called is not resolver1_supported
