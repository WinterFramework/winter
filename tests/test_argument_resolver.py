import pytest
from mock import Mock

from winter import ArgumentsResolver
from winter import GenericArgumentResolver
from winter.argument_resolver import ArgumentNotSupported
from winter.core import ComponentMethod
from winter.core import ComponentMethodArgument
from .utils import get_request


@pytest.mark.parametrize('arg_name, arg_type, resolver_arg_name, resolver_arg_type, expected_supported', [
    ('a', int, 'a', int, True),
    ('a', int, 'b', int, False),
    ('a', int, 'a', str, False),
    ('a', int, 'b', str, False),
])
def test_generic_argument_resolver_is_supported(arg_name, arg_type, resolver_arg_name, resolver_arg_type,
                                                expected_supported):
    resolve_argument_mock = Mock()
    generic_argument_resolver = GenericArgumentResolver(resolver_arg_name, resolver_arg_type, resolve_argument_mock)
    argument = ComponentMethodArgument(Mock(), arg_name, arg_type)

    # Act
    is_supported = generic_argument_resolver.is_supported(argument)

    # Assert
    assert is_supported is expected_supported
    resolve_argument_mock.assert_not_called()


def test_resolve_arguments_returns_empty_dict_for_empty_arguments():
    def func():
        pass

    expected_resolved_arguments = {}
    method = ComponentMethod(func)
    arguments_resolver = ArgumentsResolver()

    # Act
    resolved_arguments = arguments_resolver.resolve_arguments(method, http_request=Mock())

    # Assert
    assert resolved_arguments == expected_resolved_arguments


def test_resolve_arguments_resolves_argument_with_the_first_resolver():
    def func(a: int):
        pass

    expected_resolved_value = 1
    expected_resolved_arguments = {
        'a': expected_resolved_value,
    }
    method = ComponentMethod(func)
    arguments_resolver = ArgumentsResolver()
    resolver = Mock()
    resolver.is_supported.return_value = True
    resolver.resolve_argument.return_value = expected_resolved_value
    arguments_resolver.add_argument_resolver(resolver)

    # Act
    resolved_arguments = arguments_resolver.resolve_arguments(method, http_request=Mock())

    # Assert
    assert resolved_arguments == expected_resolved_arguments


def test_resolve_arguments_resolves_argument_with_the_second_resolver():
    def func(a: int):
        pass

    expected_resolved_value = 1
    expected_resolved_arguments = {
        'a': expected_resolved_value,
    }
    method = ComponentMethod(func)
    arguments_resolver = ArgumentsResolver()
    resolver1 = Mock()
    resolver1.is_supported.return_value = False
    arguments_resolver.add_argument_resolver(resolver1)
    resolver2 = Mock()
    resolver2.is_supported.return_value = True
    resolver2.resolve_argument.return_value = expected_resolved_value
    arguments_resolver.add_argument_resolver(resolver2)

    # Act
    resolved_arguments = arguments_resolver.resolve_arguments(method, http_request=Mock())

    # Assert
    assert resolved_arguments == expected_resolved_arguments


def test_resolve_arguments_fails():
    def func(a: int):
        pass

    arg_name = 'a'
    method = ComponentMethod(func)
    arguments_resolver = ArgumentsResolver()

    # Assert
    with pytest.raises(ArgumentNotSupported, match=f'Unable to resolve argument {arg_name}: int'):
        # Act
        arguments_resolver.resolve_arguments(method, http_request=Mock())


def test_arguments_resolver_is_supported_true():
    def func(self, argument: int):
        return None

    def resolve_argument(argument: ComponentMethodArgument, http_request):
        return argument.type_

    arguments_resolver = ArgumentsResolver()
    resolver = GenericArgumentResolver(
        arg_name='argument',
        arg_type=int,
        resolve_argument=resolve_argument,
    )
    arguments_resolver.add_argument_resolver(resolver)
    method = ComponentMethod(func)
    argument = method.get_argument('argument')
    request = get_request()

    # Assert
    assert arguments_resolver.is_supported(argument)
    assert arguments_resolver.resolve_argument(argument, request) == argument.type_
