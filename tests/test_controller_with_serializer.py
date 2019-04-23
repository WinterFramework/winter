from http import HTTPStatus

from rest_framework.test import APIClient

from tests.entities import AuthorizedUser


def test_controller_with_serializer():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    data = {'number': 1}
    expected_data = {'number': 2}

    response = client.post('/with-serializer/', data=data)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_data


def test_controller_with_serializer_context():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    expected_data = {'number': 123}

    response = client.get('/with-serializer/with-context/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_data
