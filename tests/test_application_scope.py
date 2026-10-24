"""
Isolation test for docs/architecture.md, principle 2: framework behaviour is never process-global.
Two applications in one process must not share behaviour: the handler of a @problem exception of one application
does not handle that exception in another.
"""
from http import HTTPStatus

from django.test import RequestFactory

import winter.django
import winter.web
from winter.application import Application
from winter.application import get_injector


@winter.web.problem(status=HTTPStatus.CONFLICT)
class _ErrorA(Exception):
    pass


class _API:
    @winter.web.route_get('raise-a/')
    def raise_a(self):
        raise _ErrorA()


def test_problem_handler_of_one_application_does_not_handle_exceptions_in_another():
    app_1 = Application(modules=[], injector=get_injector())
    app_1.add(_ErrorA)
    app_2 = Application(modules=[], injector=get_injector())
    app_2.add(_API)
    winter.django.create_urls(app_1)
    [url] = winter.django.create_urls(app_2)

    # Act
    response = url.callback(RequestFactory().get('/raise-a/'))

    # Assert
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
