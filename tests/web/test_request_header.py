from http import HTTPStatus

import pytest
from rest_framework.test import APIClient

from tests.entities import AuthorizedUser
from winter.web.request_header_annotation import request_header


def test_without_arguments():
    def method(header: str):  # pragma: no cover
        return header

    annotation_decorator = request_header('X_Header', to='invalid_header')

    with pytest.raises(AssertionError) as exception:
        annotation_decorator(method)
    assert exception.value.args == ('Not found argument "invalid_header" in "method"',)


def test_request_header():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    # Act
    response = client.post('/with-request-header/', content_type='application/json', HTTP_X_HEADER=314)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 314


def test_request_header_invalid_type():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    # Act
    response = client.post('/with-request-header/', content_type='application/json', HTTP_X_HEADER='abracadabra')

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'status': 400,
        'type': 'urn:problem-type:request-data-decode',
        'title': 'Request data decode',
        'detail': 'Failed to decode request data',
        'errors': {
            'error': 'Cannot decode "abracadabra" to integer',
        }
    }


def test_request_header_without_header():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    # Act
    response = client.post('/with-request-header/', content_type='application/json')

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'status': 400,
        'type': 'urn:problem-type:request-data-decode',
        'title': 'Request data decode',
        'detail': 'Failed to decode request data',
        'errors': {
            'error': 'Missing required header "X-Header"',
        }
    }
