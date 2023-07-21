from http import HTTPStatus

import pytest

from winter.web.argument_resolver import ArgumentNotSupported
from .api.api_with_exceptions import CustomException
from .api.api_with_exceptions import ExceptionWithoutHandler
from .entities import AuthorizedUser


@pytest.mark.parametrize(
    ['url_path', 'expected_status', 'expected_body'], (
        ('declared_but_not_thrown', HTTPStatus.OK, 'Hello, sir!'),
        ('declared_and_thrown', HTTPStatus.BAD_REQUEST, {'message': 'declared_and_thrown'}),
        ('declared_and_thrown_child', HTTPStatus.BAD_REQUEST, {'message': 'declared_and_thrown_child'}),
        ('exception_with_custom_handler', HTTPStatus.UNAUTHORIZED, 21),
    ),
)
def test_api_with_exceptions(api_client, url_path, expected_status, expected_body):
    url = f'/with_exceptions/{url_path}/'

    # Act
    response = api_client.get(url, headers={'Test-Authorize': 'user'})

    # Assert
    assert response.status_code == expected_status
    assert response.json() == expected_body


@pytest.mark.parametrize(
    ['url_path', 'expected_exception_cls'], (
        ('not_declared_but_thrown', CustomException),
        ('declared_but_no_handler', ExceptionWithoutHandler),
    ),
)
def test_api_with_exceptions_throws(api_client, url_path, expected_exception_cls):
    url = f'/with_exceptions/{url_path}/'

    # Act
    with pytest.raises(expected_exception_cls):
        api_client.get(url, headers={'Test-Authorize': 'user'})


def test_exception_handler_with_unknown_argument(api_client):
    url = '/with_exceptions/with_unknown_argument_exception/'

    # Act
    with pytest.raises(ArgumentNotSupported):
        api_client.get(url, headers={'Test-Authorize': 'user'})


@pytest.mark.parametrize(
    ['url_path', 'expected_status', 'expected_content_type', 'expected_body'], (
        (
            'problem_exists_exception',
            HTTPStatus.FORBIDDEN,
            'application/problem+json',
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
            'application/problem+json',
            {
                'status': 403,
                'type': 'urn:problem-type:problem-exists-dataclass',
                'title': 'Problem exists dataclass',
                'detail': 'Implicit string of detail dataclass',
                'custom_field': 'custom value',
            },
        ),
        (
            'all_field_const_problem_exists_exception',
            HTTPStatus.BAD_REQUEST,
            'application/problem+json',
            {
                'status': 400,
                'type': 'urn:problem-type:all-field-problem-exists',
                'title': 'All fields problem exists',
                'detail': 'A lot of interesting things happens with this problem',
            },
        ),
        (
            'inherited_problem_exists_exception',
            HTTPStatus.FORBIDDEN,
            'application/problem+json',
            {
                'status': 403,
                'type': 'urn:problem-type:inheritor-of-problem-exists',
                'title': 'Inheritor of problem exists',
                'detail': 'Implicit string of detail',
            },
        ),
        (
            'custom_handler_problem_exists_exception',
            HTTPStatus.BAD_REQUEST,
            'application/json',
            {'message': 'Implicit string of detail'},
        ),
        (
            'not_found_exception',
            HTTPStatus.NOT_FOUND,
            'application/problem+json',
            {
                'status': 404,
                'type': 'urn:problem-type:not-found',
                'title': 'Not found',
                'detail': 'MyEntity with ID=1 not found',
            },
        ),
        (
            'request_data_decoding_exception_with_str_errors',
            HTTPStatus.BAD_REQUEST,
            'application/problem+json',
            {
                'status': 400,
                'type': 'urn:problem-type:request-data-decode',
                'title': 'Request data decode',
                'detail': 'Failed to decode request data',
                'errors': {'error': 'Cannot decode "data1" to integer'},
            },
        ),
        (
            'request_data_decoding_exception_with_dict_errors',
            HTTPStatus.BAD_REQUEST,
            'application/problem+json',
            {
                'status': 400,
                'type': 'urn:problem-type:request-data-decode',
                'title': 'Request data decode',
                'detail': 'Failed to decode request data',
                'errors': {
                    'non_field_error': 'Missing fields: "id", "status", "int_status", "birthday"',
                    'contact': {
                        'phones': 'Cannot decode "123" to set',
                    },
                }
            },
        ),
    ),
)
def test_api_with_problem_exceptions(api_client, url_path, expected_status, expected_content_type, expected_body):
    url = f'/with-problem-exceptions/{url_path}/'

    # Act
    response = api_client.get(url, headers={'Test-Authorize': 'user'})

    # Assert
    assert response.status_code == expected_status
    assert response.get('Content-Type') == expected_content_type
    assert response.json() == expected_body
