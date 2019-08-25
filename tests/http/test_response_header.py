from http import HTTPStatus

from rest_framework.test import APIClient

from tests.entities import AuthorizedUser


def test_response_header():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    # Act
    response = client.get('/with-response-headers/one-header/', content_type='application/json')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response['x-header1'] == 'test header'
