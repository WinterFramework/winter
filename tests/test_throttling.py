import datetime
from http import HTTPStatus

import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient

from .entities import AuthorizedUser


@pytest.mark.parametrize('need_auth', (True, False))
def test_throttling(need_auth):
    client = APIClient()

    if need_auth:
        user = AuthorizedUser()
        client.force_authenticate(user)

    for i in range(1, 5):
        response = client.get('/with-throttling-on-controller/')
        response_of_same = client.get('/with-throttling-on-controller/same/')

        if i > 6 // 2:
            assert response.status_code == response_of_same.status_code == HTTPStatus.TOO_MANY_REQUESTS, i
        else:
            assert response.status_code == response_of_same.status_code == HTTPStatus.OK, i


def test_throttling_discards_old_requests():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    with freeze_time(datetime.datetime(2000, 1, 1, second=0, microsecond=0)):
        for _ in range(3):
            client.get('/with-throttling-on-controller/')

    with freeze_time(datetime.datetime(2000, 1, 1, second=0, microsecond=600000)):
        for _ in range(2):
            client.get('/with-throttling-on-controller/')

    # Act
    with freeze_time(datetime.datetime(2000, 1, 1, second=1, microsecond=0)):
        response = client.get('/with-throttling-on-controller/')

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('need_auth', (True, False))
def test_throttling_on_method(need_auth):
    client = APIClient()
    if need_auth:
        user = AuthorizedUser()
        client.force_authenticate(user)

    for i in range(1, 10):
        response = client.get('/with-throttling-on-method/')
        response_of_same = client.get('/with-throttling-on-method/same/')
        if i > 5:
            assert response.status_code == response_of_same.status_code == HTTPStatus.TOO_MANY_REQUESTS, i
        else:
            assert response.status_code == response_of_same.status_code == HTTPStatus.OK, i


@pytest.mark.parametrize(('url', 'method'), (
    ('/with-throttling-on-method/without-throttling/', 'get'),
    ('/with-throttling-on-controller/', 'post'),
))
def test_throttling_without_throttling(url, method):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    for i in range(1, 10):
        client_method = getattr(client, method)
        response = client_method(url)
        assert response.status_code == HTTPStatus.OK, i
