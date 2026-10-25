import json
from dataclasses import dataclass
from http import HTTPStatus

import injector
import pytest
from django.http import HttpRequest
from django.test import RequestFactory
from mock import patch

import winter.django
import winter.web
from winter.application import Application
from winter.web import interceptor_registry


class _Visit:
    def __init__(self, number: int, path: str):
        self.number = number
        self.path = path


class _VisitModule(injector.Module):
    def __init__(self):
        self._visits = 0

    @injector.provider
    @winter.web.request_scope
    def visit(self, request: HttpRequest) -> _Visit:
        self._visits += 1
        return _Visit(self._visits, request.path)


class _VisitAPI:
    @winter.web.route_get('visit/')
    def get(self, visit: _Visit, same_visit: _Visit, request: winter.web.Request) -> dict:
        return {'number': visit.number, 'path': visit.path, 'same': visit is same_visit, 'method': request.method}


def _create_urls(*definitions, app_injector=None):
    app = Application(modules=[], injector=app_injector or injector.Injector())
    for definition in definitions:
        app.add(definition)
    return winter.django.create_urls(app)


def _get(url, path: str):
    return url.callback(RequestFactory().get(path))


def test_request_scoped_value_is_created_once_per_request():
    [url] = _create_urls(_VisitAPI, app_injector=injector.Injector([_VisitModule()]))

    # Act
    first_response = _get(url, '/visit/')
    second_response = _get(url, '/visit/')

    # Assert
    assert json.loads(first_response.content) == {'number': 1, 'path': '/visit/', 'same': True, 'method': 'GET'}
    assert json.loads(second_response.content) == {'number': 2, 'path': '/visit/', 'same': True, 'method': 'GET'}


class _VisitInterceptor(winter.web.Interceptor):
    def __init__(self):
        self.visits = []

    def pre_handle(self, visit: _Visit):
        self.visits.append(visit)


class _VisitNumberAPI:
    @winter.web.route_get('visit/')
    def get(self, visit: _Visit) -> int:
        return visit.number


def test_interceptor_and_api_method_get_same_request_scoped_value():
    interceptor = _VisitInterceptor()
    with patch.object(interceptor_registry, '_interceptors', [interceptor]):
        [url] = _create_urls(_VisitNumberAPI, app_injector=injector.Injector([_VisitModule()]))

        # Act
        response = _get(url, '/visit/')

    # Assert
    assert response.content == b'1'
    assert [visit.number for visit in interceptor.visits] == [1]


def test_request_scoped_value_does_not_exist_outside_request():
    app_injector = injector.Injector([_VisitModule()])

    # Act
    with pytest.raises(LookupError) as exception_info:
        app_injector.get(_Visit)

    # Assert
    assert str(exception_info.value) == '_Visit is request-scoped: it exists only while Winter handles a request'


@dataclass
class _NewTodo:
    title: str = ''


class _TodoAPI:
    @winter.web.route_post('todos/')
    def create(self, todo: _NewTodo):  # pragma: no cover
        pass


def test_argument_neither_mapped_from_request_nor_bound_fails_startup():
    # Act
    with pytest.raises(TypeError) as exception_info:
        _create_urls(_TodoAPI)

    # Assert
    assert str(exception_info.value) == (
        '_TodoAPI.create: argument todo (_NewTodo) is not mapped from the request and has no binding in the injector'
    )


class _ResponseHeaderAPI:
    @winter.web.route_get('header/')
    def get(self, header: winter.web.ResponseHeader[str]):  # pragma: no cover
        pass


def test_response_header_without_annotation_fails_startup():
    # Act
    with pytest.raises(TypeError) as exception_info:
        _create_urls(_ResponseHeaderAPI)

    # Assert
    assert str(exception_info.value) == (
        '_ResponseHeaderAPI.get: argument header (ResponseHeader[str]) is not mapped from the request '
        'and has no binding in the injector'
    )


class _ExceptionHandlers:
    @winter.web.exception_handler
    def handle(self, exception: LookupError, todo: _NewTodo):  # pragma: no cover
        pass


def test_exception_handler_argument_neither_mapped_nor_bound_fails_startup():
    # Act
    with pytest.raises(TypeError) as exception_info:
        _create_urls(_ExceptionHandlers)

    # Assert
    assert str(exception_info.value) == (
        '_ExceptionHandlers.handle: argument todo (_NewTodo) is not mapped from the request '
        'and has no binding in the injector'
    )


class _TodoInterceptor(winter.web.Interceptor):
    def pre_handle(self, todo: _NewTodo):  # pragma: no cover
        pass


def test_interceptor_argument_neither_mapped_nor_bound_fails_startup():
    with patch.object(interceptor_registry, '_interceptors', [_TodoInterceptor()]):
        # Act
        with pytest.raises(TypeError) as exception_info:
            _create_urls()

    # Assert
    assert str(exception_info.value) == (
        '_TodoInterceptor.pre_handle: argument todo (_NewTodo) is not mapped from the request '
        'and has no binding in the injector'
    )


def test_interceptor_added_after_startup_does_not_get_unbound_argument():
    [url] = _create_urls(_VisitNumberAPI, app_injector=injector.Injector([_VisitModule()]))

    with patch.object(interceptor_registry, '_interceptors', [_TodoInterceptor()]):
        # Act
        response = _get(url, '/visit/')

    # Assert
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
