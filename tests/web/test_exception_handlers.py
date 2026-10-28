from http import HTTPStatus

import pytest
from django.test import RequestFactory

import winter.django
import winter.web
from tests.injection import app_injector
from winter.web.exceptions import RedirectException


class _BaseError(Exception):
    pass


class _ChildError(_BaseError):
    pass


class _GrandChildError(_ChildError):
    pass


class _OtherError(Exception):
    pass


def _raising(exception: Exception):
    class _API:
        @winter.web.route_get('raise/')
        def raise_(self):
            raise exception

    return _API


def _get(*definitions):
    app = winter.web.WebApplication(modules=[], injector=app_injector)
    for definition in definitions:
        app.add(definition)
    [url] = winter.django.create_urls(app)
    return url.callback(RequestFactory().get('/raise/'))


class _ExceptionHandler:
    @winter.web.exception_handler
    @winter.web.response_status(HTTPStatus.SERVICE_UNAVAILABLE)
    def handle(self, exception: Exception) -> str:
        return 'handled by the application'


def test_handler_of_application_replaces_built_in_handler_of_same_exception():
    # Act
    response = _get(_raising(_OtherError()), _ExceptionHandler)

    # Assert
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.content == b'"handled by the application"'


def test_built_in_handler_of_nearer_exception_is_not_replaced():
    # Act
    response = _get(_raising(RedirectException('/elsewhere/')), _ExceptionHandler)

    # Assert
    assert response.status_code == HTTPStatus.FOUND
    assert response['Location'] == '/elsewhere/'


class _Handlers:
    @winter.web.exception_handler
    def handle_base(self, exception: _BaseError) -> str:
        return 'base'

    @winter.web.exception_handler
    def handle_child(self, exception: _ChildError) -> str:
        return 'child'


@pytest.mark.parametrize('exception, expected_content', [
    (_BaseError(), b'"base"'),
    (_ChildError(), b'"child"'),
    (_GrandChildError(), b'"child"'),
])
def test_handler_of_nearest_class_in_mro_handles_exception(exception, expected_content):
    # Act
    response = _get(_raising(exception), _Handlers)

    # Assert
    assert response.content == expected_content


class _UnionHandler:
    @winter.web.exception_handler
    def handle(self, error: _ChildError | _OtherError) -> str:
        return type(error).__name__


@pytest.mark.parametrize('exception, expected_content', [
    (_ChildError(), b'"_ChildError"'),
    (_OtherError(), b'"_OtherError"'),
])
def test_handler_annotated_with_union_handles_each_exception(exception, expected_content):
    # Act
    response = _get(_raising(exception), _UnionHandler)

    # Assert
    assert response.content == expected_content


class _FailingHandlers:
    @winter.web.exception_handler
    def handle_other(self, exception: _OtherError):
        raise _BaseError()

    @winter.web.exception_handler
    def handle_base(self, exception: _BaseError) -> str:  # pragma: no cover
        return 'base'


def test_exception_of_failing_handler_goes_to_handler_of_exception():
    # Act
    response = _get(_raising(_OtherError()), _FailingHandlers)

    # Assert
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.content == b'Server Error (500)'


class _RetryHandler:
    @winter.web.exception_handler
    @winter.web.response_header('Retry-After', 'retry_after')
    @winter.web.response_status(HTTPStatus.SERVICE_UNAVAILABLE)
    def handle(self, exception: _OtherError, retry_after: winter.web.ResponseHeader[int]):
        retry_after.set(30)


def test_handler_sets_response_header():
    # Act
    response = _get(_raising(_OtherError()), _RetryHandler)

    # Assert
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response['Retry-After'] == '30'


def test_two_handlers_of_same_exception_in_application_fail_startup():
    class _OtherHandlers:
        @winter.web.exception_handler
        def handle(self, exception: _BaseError):  # pragma: no cover
            pass

    # Act
    with pytest.raises(ValueError) as exception_info:
        _get(_raising(_BaseError()), _Handlers, _OtherHandlers)

    # Assert
    assert str(exception_info.value) == '_BaseError has two handlers: _Handlers.handle_base and _OtherHandlers.handle'


def _not_annotated(self, exception):  # pragma: no cover
    pass


def _not_an_exception(self, exception: str):  # pragma: no cover
    pass


def _without_arguments(self):  # pragma: no cover
    pass


@pytest.mark.parametrize('handle', [_not_annotated, _not_an_exception, _without_arguments])
def test_handler_without_exception_as_first_argument_fails_startup(handle):
    handlers = type('_InvalidHandlers', (), {'handle': winter.web.exception_handler(handle)})

    # Act
    with pytest.raises(TypeError) as exception_info:
        _get(_raising(_BaseError()), handlers)

    # Assert
    assert str(exception_info.value) == (
        '_InvalidHandlers.handle: the first argument of an exception handler must be annotated '
        'with the exceptions it handles'
    )
