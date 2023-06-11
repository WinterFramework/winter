import json
from http import HTTPStatus

import pytest
from rest_framework.test import APIClient

from tests.entities import AuthorizedUser
from winter import request_body


def test_request_body():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    data = {
        'id': 1,
        'name': 'test name',
        'is_god': True,
        'status': 'active',
        'items': [1, 2],
    }
    expected_data = {
        'id': 1,
        'with_default': 5,
        'name': 'test name',
        'is_god': True,
        'status': 'active',
        'optional_status': None,
        'items': [1, 2],
        'optional_items': None,
    }
    data = json.dumps(data)

    # Act
    response = client.post('/with-request-data/', data=data, content_type='application/json')

    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json() == expected_data


def test_request_body_as_list():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    data = [{
        'id': 1,
        'name': 'test name',
        'is_god': True,
        'status': 'active',
        'items': [1, 2],
    }]
    expected_data = [{
        'id': 1,
        'with_default': 5,
        'name': 'test name',
        'is_god': True,
        'status': 'active',
        'optional_status': None,
        'items': [1, 2],
        'optional_items': None,
    }]
    data = json.dumps(data)

    # Act
    response = client.post('/with-request-data/many/', data=data, content_type='application/json')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_data


def test_request_body_with_errors():
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
        'status': 400,
        'type': 'urn:problem-type:request-data-decode',
        'title': 'Request data decode',
        'detail': 'Failed to decode request data',
        'errors': {
            'id': 'Cannot decode "invalid integer" to integer',
            'status': 'Value not in allowed values("active", "super_active"): "invalid status"',
            'items': 'Cannot decode "invalid integer" to integer',
            'non_field_error': 'Missing fields: "name"',
        }
    }
    data = json.dumps(data)

    # Act
    response = client.post('/with-request-data/', data=data, content_type='application/json')

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == expected_data


def test_without_argument():
    def method(argument: int):  # pragma: no cover
        return argument

    annotation_decorator = request_body('invalid_argument')

    with pytest.raises(AssertionError) as exception:
        annotation_decorator(method)
    assert exception.value.args == ('Not found argument "invalid_argument" in "method"',)
