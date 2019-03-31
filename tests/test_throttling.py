from http import HTTPStatus

import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient

from .entities import AuthorizedUser


def test_throttling():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    for i in range(1, 10):
        response = client.get('/with-throttling-on-controller/')
        if i > 5:
            assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS, i
        else:
            assert response.status_code == HTTPStatus.OK, i


def test_throttling_discards_old_requests():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    with freeze_time('2000-01-01 10:00:00'):
        for _ in range(10):
            client.get('/with-throttling-on-controller/')

    # Act
    with freeze_time('2000-01-01 10:00:30'):
        response = client.get('/with-throttling-on-controller/')

    assert response.status_code == HTTPStatus.OK


def test_throttling_on_method():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    for i in range(1, 10):
        response = client.get('/with-throttling-on-method/')
        if i > 5:
            assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS, i
        else:
            assert response.status_code == HTTPStatus.OK, i


@pytest.mark.parametrize(('url', 'method'), (
        ('/with-throttling-on-method/without-throttling/', 'get'),
        ('/with-throttling-on-controller/', 'post')
))
def test_throttling_without_throttling(url, method):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    for i in range(1, 10):
        client_method = getattr(client, method)
        response = client_method(url)
        assert response.status_code == HTTPStatus.OK, i
