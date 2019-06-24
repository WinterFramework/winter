from http import HTTPStatus

from rest_framework.test import APIClient

from tests.entities import AuthorizedUser


def test_input_data():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    data = {
        'id': 1,
        'name': 'test name',
        'is_god': True,
        'status': 'active',
    }
    expected_data = data.copy()

    # Act
    response = client.post('/with-input-data/', data=data)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_data


def test_input_data_with_errors():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    data = {
        'id': 'invalid integer',
        'name': 'test name',
        'is_god': False,
        'status': 'invalid status',
    }

    expected_data = {
        'id': 'value is not a valid integer',
        'status': 'value is not a valid enumeration member',
    }

    # Act
    response = client.post('/with-input-data/', data=data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == expected_data
