from http import HTTPStatus

from rest_framework.test import APIClient

from tests.entities import AuthorizedUser


def test_controller_with_serializer():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    response = client.get('/with-redirect-exception/')

    assert response.status_code == HTTPStatus.FOUND
    assert response.content == b''
    assert response['Location'] == 'http://1.2.3.4/'
