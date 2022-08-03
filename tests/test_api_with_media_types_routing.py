from http import HTTPStatus

from rest_framework.test import APIClient

from tests.entities import AuthorizedUser


def test_api_with_media_types_routing_returns_200():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    response = client.get('/with-media-types-routing/xml/', headers={'Accept': 'application/xml'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'Hello, sir!'
