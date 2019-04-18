from http import HTTPStatus

from rest_framework.test import APIClient

from tests.entities import AuthorizedUser


def test_controller_with_limits_with_redirect_to_default_redirects():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    response = client.get('/with-limits/with-redirect-to-default/')

    assert response.status_code == HTTPStatus.FOUND
    assert response['Location'] == '/with-limits/with-redirect-to-default/?limit=20'


def test_controller_with_limits_with_redirect_to_default_ok():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    response = client.get('/with-limits/with-redirect-to-default/?limit=30')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'limit': 30, 'offset': None}
