import pytest
from mock import Mock

from winter import ArgumentsResolver
from winter.core import ComponentMethod
from winter.web.argument_resolver import ArgumentNotSupported


def test_resolve_arguments_returns_empty_dict_for_empty_arguments():
    def func():  # pragma: no cover
        pass

    expected_resolved_arguments = {}
    method = ComponentMethod(func)
    arguments_resolver = ArgumentsResolver()

    # Act
    resolved_arguments = arguments_resolver.resolve_arguments(method, request=Mock(), response_headers={})

    # Assert
    assert resolved_arguments == expected_resolved_arguments


def test_resolve_arguments_resolves_argument_with_the_first_resolver():
    def func(a: int):  # pragma: no cover
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
    resolved_arguments = arguments_resolver.resolve_arguments(method, request=Mock(), response_headers={})

    # Assert
    assert resolved_arguments == expected_resolved_arguments


def test_resolve_arguments_resolves_argument_with_the_second_resolver():
    def func(a: int):  # pragma: no cover
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
    resolved_arguments = arguments_resolver.resolve_arguments(method, request=Mock(), response_headers={})

    # Assert
    assert resolved_arguments == expected_resolved_arguments


def test_resolve_arguments_fails():
    def func(a: int):  # pragma: no cover
        pass

    arg_name = 'a'
    method = ComponentMethod(func)
    arguments_resolver = ArgumentsResolver()

    # Assert
    with pytest.raises(ArgumentNotSupported, match=f'Unable to resolve argument {arg_name}: int'):
        # Act
        arguments_resolver.resolve_arguments(method, request=Mock(), response_headers={})
