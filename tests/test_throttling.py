import pytest
from rest_framework.test import APIClient

from .entities import AuthorizedUser


def test_throttling():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    for i in range(1, 10):
        response = client.get('/with-throttling-on-controller/')
        if i > 5:
            assert response.status_code == 429, i
        else:
            assert response.status_code == 200, i


def test_throttling_on_method():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    for i in range(1, 10):
        response = client.get('/with-throttling-on-method/')
        if i > 5:
            assert response.status_code == 429, i
        else:
            assert response.status_code == 200, i


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
        assert response.status_code == 200, i
