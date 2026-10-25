import pytest
from injector import Injector
from mock import Mock

from winter.components import ComponentMethod
from winter.web import Request
from winter.web.argument_resolver import ArgumentsResolver
from winter.web.request_scope import create_request_injector


class _Dependency:
    pass


def _resolver(is_supported: bool, value=None):
    resolver = Mock()
    resolver.is_supported.return_value = is_supported
    resolver.resolve_argument.return_value = value
    return resolver


def _resolve(arguments_resolver: ArgumentsResolver, func, app_injector=None, context=None):
    request_injector = create_request_injector(app_injector or Injector(), Mock(spec=Request), {})
    return arguments_resolver.resolve_arguments(ComponentMethod(func), Mock(), {}, request_injector, context)


def test_resolve_arguments_returns_empty_dict_for_empty_arguments():
    def func():  # pragma: no cover
        pass

    # Act
    resolved_arguments = _resolve(ArgumentsResolver([]), func)

    # Assert
    assert resolved_arguments == {}


def test_first_resolver_that_supports_argument_resolves_it():
    def func(a: int):  # pragma: no cover
        pass

    arguments_resolver = ArgumentsResolver([_resolver(False), _resolver(True, 1), _resolver(True, 2)])

    # Act
    resolved_arguments = _resolve(arguments_resolver, func)

    # Assert
    assert resolved_arguments == {'a': 1}


def test_context_value_is_taken_before_resolvers():
    def func(a: int):  # pragma: no cover
        pass

    # Act
    resolved_arguments = _resolve(ArgumentsResolver([_resolver(True, 1)]), func, context={'a': 2})

    # Assert
    assert resolved_arguments == {'a': 2}


def test_argument_that_no_resolver_supports_comes_from_injector():
    def func(dependency: _Dependency):  # pragma: no cover
        pass

    dependency = _Dependency()
    app_injector = Injector([lambda binder: binder.bind(_Dependency, to=dependency)])

    # Act
    resolved_arguments = _resolve(ArgumentsResolver([_resolver(False)]), func, app_injector)

    # Assert
    assert resolved_arguments == {'dependency': dependency}


def test_argument_that_injector_only_can_create_is_not_resolved():
    def func(dependency: _Dependency):  # pragma: no cover
        pass

    # Act
    with pytest.raises(TypeError) as exception_info:
        _resolve(ArgumentsResolver([]), func)

    # Assert
    assert str(exception_info.value) == (
        'test_argument_that_injector_only_can_create_is_not_resolved.<locals>.func: argument dependency (_Dependency) '
        'is not mapped from the request and has no binding in the injector'
    )


@pytest.mark.parametrize('request_types, context_names', [
    ([_Dependency], ()),
    ((), ['dependency']),
])
def test_check_accepts_request_types_and_context_names(request_types, context_names):
    def func(dependency: _Dependency):  # pragma: no cover
        pass

    # Act
    ArgumentsResolver([]).check_arguments(ComponentMethod(func), Injector(), request_types, context_names)


def test_check_accepts_binding_of_parent_injector():
    def func(dependency: _Dependency):  # pragma: no cover
        pass

    parent_injector = Injector([lambda binder: binder.bind(_Dependency)])

    # Act
    ArgumentsResolver([]).check_arguments(ComponentMethod(func), parent_injector.create_child_injector(), ())
