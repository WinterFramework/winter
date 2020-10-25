from http import HTTPStatus

import pytest
from rest_framework.test import APIClient

from winter.web.argument_resolver import ArgumentNotSupported
from .controllers.controller_with_exceptions import CustomException
from .controllers.controller_with_exceptions import ExceptionWithoutHandler
from .controllers.controller_with_problem_exceptions import ProblemExistsException
from .entities import AuthorizedUser


@pytest.mark.parametrize(
    ['url_path', 'expected_status', 'expected_body'], (
        ('declared_but_not_thrown', HTTPStatus.OK, 'Hello, sir!'),
        ('declared_and_thrown', HTTPStatus.BAD_REQUEST, {'message': 'declared_and_thrown'}),
        ('declared_and_thrown_child', HTTPStatus.BAD_REQUEST, {'message': 'declared_and_thrown_child'}),
        ('exception_with_custom_handler', HTTPStatus.UNAUTHORIZED, 21),
    ),
)
def test_controller_with_exceptions(url_path, expected_status, expected_body):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    url = f'/controller_with_exceptions/{url_path}/'

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == expected_status
    assert response.json() == expected_body


@pytest.mark.parametrize(
    ['url_path', 'expected_exception_cls'], (
        ('not_declared_but_thrown', CustomException),
        ('declared_but_no_handler', ExceptionWithoutHandler),
    ),
)
def test_controller_with_exceptions_throws(url_path, expected_exception_cls):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    url = f'/controller_with_exceptions/{url_path}/'

    # Act
    with pytest.raises(expected_exception_cls):
        client.get(url)


def test_exception_handler_with_unknown_argument():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    url = '/controller_with_exceptions/with_unknown_argument_exception/'

    # Act
    with pytest.raises(ArgumentNotSupported):
        client.get(url)


@pytest.mark.parametrize(
    ['url_path', 'expected_status', 'expected_body'], (
        (
            'problem_exists_exception',
            HTTPStatus.FORBIDDEN,
            {
                'detail': 'Implicit string of detail',
                'status': 403,
                'title': 'Problem exists',
                'type': 'urn:problem-type:problem-exists',
            },
        ),
        (
            'problem_exists_dataclass_exception',
            HTTPStatus.FORBIDDEN,
            {
                'status': 403,
                'type': 'urn:problem-type:problem-exists-dataclass',
                'title': 'Problem exists dataclass',
                'detail': 'Implicit string of detail dataclass',
                'custom_field': 'custom value',
            },
        ),
        (
            'problem_exists_auto_handle_exception',
            HTTPStatus.FORBIDDEN,
            {
                'status': 403,
                'type': 'urn:problem-type:problem-exists-auto-handle',
                'title': 'Problem exists auto handle',
                'detail': '',
            },
        ),
        (
            'custom_handler_problem_exists_exception',
            HTTPStatus.BAD_REQUEST,
            {'message': 'Implicit string of detail'},
        ),
    ),
)
def test_controller_with_problem_exceptions(url_path, expected_status, expected_body):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    url = f'/controller_with_problem_exceptions/{url_path}/'

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == expected_status
    assert response.json() == expected_body


@pytest.mark.parametrize(
    ['url_path', 'expected_exception_cls'], (
        ('problem_exists_not_handled_exception', ProblemExistsException),
    ),
)
def test_controller_with_problem_exceptions_raise_error(url_path, expected_exception_cls):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    url = f'/controller_with_problem_exceptions/{url_path}/'

    # Act
    with pytest.raises(expected_exception_cls):
        client.get(url)
