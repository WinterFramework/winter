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
        'items': [1],
    }
    expected_data = {
        'id': 1,
        'with_default': 5,
        'name': 'test name',
        'is_god': True,
        'status': 'active',
        'optional_status': None,
        'items': [1],
        'optional_items': None,
    }

    # Act
    response = client.post('/with-input-data/', data=data)

    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json() == expected_data


def test_input_data_with_errors():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    data = {
        'id': 'invalid integer',
        'is_god': False,
        'status': 'invalid status',
        'invalid_key': 'data',
        'items': ['invalid integer'],
    }

    expected_data = {
        'id': 'value is not a valid integer',
        'status': 'value is not a valid enumeration member',
        'items': 'value is not a valid integer',
        'non_field_error': 'Missing fields: name',
    }

    # Act
    response = client.post('/with-input-data/', data=data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == expected_data
