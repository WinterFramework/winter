"""
Isolation test for docs/architecture.md, principle 2: framework behaviour is never process-global.
Two applications in one process must not share behaviour: the handler of a @problem exception of one application
does not handle that exception in another, the arguments of an API method come from the injector of the
application that serves it, and an interceptor of one application does not run in another.
"""
from http import HTTPStatus

from django.test import RequestFactory
from injector import Injector

import winter.django
import winter.web
from winter.application import get_injector


@winter.web.problem(status=HTTPStatus.CONFLICT)
class _ErrorA(Exception):
    pass


class _API:
    @winter.web.route_get('raise-a/')
    def raise_a(self):
        raise _ErrorA()


def test_problem_handler_of_one_application_does_not_handle_exceptions_in_another():
    app_1 = winter.web.WebApplication(modules=[], injector=get_injector())
    app_1.add(_ErrorA)
    app_2 = winter.web.WebApplication(modules=[], injector=get_injector())
    app_2.add(_API)
    winter.django.create_urls(app_1)
    [url] = winter.django.create_urls(app_2)

    # Act
    response = url.callback(RequestFactory().get('/raise-a/'))

    # Assert
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


class _Name:
    def __init__(self, value: str):
        self.value = value


class _NameAPI:
    @winter.web.route_get('name/')
    def get(self, name: _Name) -> str:
        return name.value


def _application_with_name(value: str) -> winter.web.WebApplication:
    app = winter.web.WebApplication(modules=[], injector=Injector([lambda binder: binder.bind(_Name, to=_Name(value))]))
    app.add(_NameAPI)
    return app


def test_argument_of_api_method_comes_from_injector_of_its_application():
    [url_1] = winter.django.create_urls(_application_with_name('one'))
    [url_2] = winter.django.create_urls(_application_with_name('two'))

    # Act
    response_1 = url_1.callback(RequestFactory().get('/name/'))
    response_2 = url_2.callback(RequestFactory().get('/name/'))

    # Assert
    assert response_1.content == b'"one"'
    assert response_2.content == b'"two"'


class _RejectingInterceptor(winter.web.Interceptor):
    def pre_handle(self):
        raise _ErrorA()


class _OKAPI:
    @winter.web.route_get('ok/')
    def get(self) -> str:
        return 'ok'


def test_interceptor_of_one_application_does_not_run_in_another():
    app_1 = winter.web.WebApplication(modules=[], interceptors=[_RejectingInterceptor])
    app_1.add(_OKAPI)
    app_2 = winter.web.WebApplication(modules=[])
    app_2.add(_OKAPI)
    [url_1] = winter.django.create_urls(app_1)
    [url_2] = winter.django.create_urls(app_2)

    # Act
    response_1 = url_1.callback(RequestFactory().get('/ok/'))
    response_2 = url_2.callback(RequestFactory().get('/ok/'))

    # Assert
    assert response_1.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response_2.content == b'"ok"'
