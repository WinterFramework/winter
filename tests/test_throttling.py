from http import HTTPStatus

import pytest
from rest_framework.test import APIClient

from .entities import AuthorizedUser


@pytest.mark.parametrize('need_auth', (True, False))
def test_throttling(need_auth):
    client = APIClient()
    if need_auth:
        user = AuthorizedUser()
        client.force_authenticate(user)

    for i in range(1, 10):
        response = client.get('/with-throttling/')
        response_of_same = client.get('/with-throttling/same/')
        if i > 5:
            assert response.status_code == response_of_same.status_code == HTTPStatus.TOO_MANY_REQUESTS, i
        else:
            assert response.status_code == response_of_same.status_code == HTTPStatus.OK, i


def test_throttling_without_throttling():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    for i in range(1, 10):
        client_method = getattr(client, 'get')
        response = client_method('/with-throttling/without-throttling/')
        assert response.status_code == HTTPStatus.OK, i
