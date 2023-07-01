from http import HTTPStatus

import pytest
from rest_framework.test import APIClient

from .entities import AuthorizedUser
from .entities import User


@pytest.mark.parametrize(['data', 'expected_body'], (
    ({'name': 'Winter'}, 'Hello, Winter!'),
    ({'name': 'Stranger'}, 'Hello, Stranger!'),
    ({}, 'Hello, stranger!'),
))
def test_simple_api(data, expected_body):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    response = client.get('/winter-simple/', data=data)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_body


def test_401_not_authenticated():
    client = APIClient()
    response = client.get('/winter-simple/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_403_forbidden():
    client = APIClient()
    user = User()
    client.force_authenticate(user)
    response = client.get('/winter-simple/')
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_get_response_entity():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    response = client.get('/winter-simple/get-response-entity/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'number': 123,
    }


@pytest.mark.parametrize(('limit', 'offset', 'expected_previous', 'expected_next'), (
    (1, 1, 'http://testserver/winter-simple/page-response/?limit=1', 'http://testserver/winter-simple/page-response/?limit=1&offset=2'),
    (None, None, None, None),
    (2, 3, 'http://testserver/winter-simple/page-response/?limit=2&offset=1', 'http://testserver/winter-simple/page-response/?limit=2&offset=5'),
    (9, 3, 'http://testserver/winter-simple/page-response/?limit=9', None),
))
def test_page_response(limit, offset, expected_previous, expected_next):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    url = f'/winter-simple/page-response/?'
    if limit is not None:
        url += f'&limit={limit}'
    if offset is not None:
        url += f'&offset={offset}'

    expected_body = {
        'objects': [{'number': 1}],
        'meta': {
            'limit': limit,
            'offset': offset,
            'next': expected_next,
            'previous': expected_previous,
            'total_count': 10,
        },
    }

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == HTTPStatus.OK, response.content
    assert response.json() == expected_body


def test_custom_page_response():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    expected_body = {
        'objects': [1, 2],
        'meta': {
            'limit': 2,
            'offset': 2,
            'next': 'http://testserver/winter-simple/custom-page-response/?limit=2&offset=4',
            'previous': 'http://testserver/winter-simple/custom-page-response/?limit=2',
            'total_count': 10,
            'extra': 456,
        },
    }
    request_data = {
        'limit': 2,
        'offset': 2,
    }

    # Act
    response = client.get('/winter-simple/custom-page-response/', data=request_data)

    # Assert
    assert response.status_code == HTTPStatus.OK, response.content
    assert response.json() == expected_body


def test_no_authentication_api():
    client = APIClient()
    response = client.get('/winter-no-auth/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'Hello, World!'


def test_return_response():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    response = client.get('/winter-simple/return-response/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'logged_in': True}


@pytest.mark.parametrize(('method', 'http_response_status'), (
    ('get', HTTPStatus.OK),
    ('post', HTTPStatus.OK),
    ('patch', HTTPStatus.OK),
    ('delete', HTTPStatus.NO_CONTENT),
    ('put', HTTPStatus.OK),
))
def test_methods(method, http_response_status):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    url = f'/winter-simple/{method}/'
    response = getattr(client, method)(url)
    assert response.status_code == http_response_status
    assert response.content == b''
