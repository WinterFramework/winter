from rest_framework.test import APIClient

from .entities import AuthorizedUser


def test_throttling():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    for i in range(1, 10):
        response = client.get('/with-throttling/')
        if i > 5:
            assert response.status_code == 429
        else:
            assert response.status_code == 200


def test_throttling_on_method():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    for i in range(1, 10):
        response = client.get('/with-throttling-on-method/')
        if i > 5:
            assert response.status_code == 429
        else:
            assert response.status_code == 200
