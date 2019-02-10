import uuid

import pytest
from rest_framework.test import APIClient

from .entities import AuthorizedUser
from .entities import User


@pytest.mark.parametrize(['data', 'expected_body'], (
        ({'name': 'Winter'}, 'Hello, Winter!'),
        ({'name': 'Stranger'}, 'Hello, Stranger!'),
        ({}, 'Hello, stranger!'),
))
def test_simple_controller(data, expected_body):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    response = client.get('/winter_simple/', data=data)
    assert response.status_code == 200
    assert response.json() == expected_body


def test_401_not_authenticated():
    client = APIClient()
    response = client.get('/winter_simple/')
    assert response.status_code == 401


def test_403_forbidden():
    client = APIClient()
    user = User()
    client.force_authenticate(user)
    response = client.get('/winter_simple/')
    assert response.status_code == 403


def test_page_response():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    expected_body = {
        'objects': [{'number': 1}],
        'meta': {
            'limit': 2,
            'offset': 2,
            'next': 'http://testserver/winter_simple/page-response/?limit=2&offset=4',
            'previous': 'http://testserver/winter_simple/page-response/?limit=2',
            'total_count': 10,
        },
    }
    data = {
        'limit': 2,
        'offset': 2,
    }

    # Act
    response = client.get('/winter_simple/page-response/', data=data)

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_body


def test_no_authentication_controller():
    client = APIClient()
    response = client.get('/winter_no_auth/')
    assert response.status_code == 200
    assert response.json() == 'Hello, World!'


uuid_ = str(uuid.uuid4())


@pytest.mark.parametrize(('url', 'expected_value'), (
        ('/with-param/1/', {
            'type': 'enum',
            'param': '1'
        }),
        ('/with-param/5/', {
            'type': 'int',
            'param': 5
        }),
        ('/with-param/test/', {
            'type': 'str',
            'param': 'test'
        }),
        (f'/with-param/{uuid_}/', {
            'type': 'uuid',
            'param': uuid_
        }),
))
def test_with_param(url, expected_value):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == expected_value
