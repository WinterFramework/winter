import json
from http import HTTPStatus

import pytest
from winter import request_body


def test_request_body(api_client):
    data = {
        'id': 1,
        'name': 'test name',
        'is_god': True,
        'status': 'active',
        'items': [1, 2],
        'items_alias': [1, 2],
        'typed_dict': {
            'field': 'field',
            'required_field': 1,
            'optional_field': 2,
        },
    }
    expected_data = {
        'id': 1,
        'with_default': 5,
        'name': 'test name',
        'is_god': True,
        'status': 'active',
        'optional_status': None,
        'optional_status_new_typing_style': None,
        'items': [1, 2],
        'items_alias': [1, 2],
        'optional_items': None,
        'optional_items_new_typing_style': None,
        'typed_dict': {
            'field': 'field',
            'required_field': 1,
            'optional_field': 2,
        },
    }

    # Act
    response = api_client.post('/with-request-data/', json=data)

    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json() == expected_data


def test_request_body_as_list(api_client):
    data = [{
        'id': 1,
        'name': 'test name',
        'is_god': True,
        'status': 'active',
        'items': [1, 2],
        'items_alias': [1, 2],
        'typed_dict': {
            'field': 'field',
            'required_field': 1,
            'optional_field': 2,
        },
    }]
    expected_data = [{
        'id': 1,
        'with_default': 5,
        'name': 'test name',
        'is_god': True,
        'status': 'active',
        'optional_status': None,
        'optional_status_new_typing_style': None,
        'items': [1, 2],
        'items_alias': [1, 2],
        'optional_items': None,
        'optional_items_new_typing_style': None,
        'typed_dict': {
            'field': 'field',
            'required_field': 1,
            'optional_field': 2,
        },
    }]

    # Act
    response = api_client.post('/with-request-data/many/', json=data)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_data


def test_request_body_with_errors(api_client):
    data = {
        'id': 'invalid integer',
        'is_god': False,
        'status': 'invalid status',
        'invalid_key': 'data',
        'items': ['invalid integer'],
        'items_alias': ['invalid integer'],
        'typed_dict': {
            'field': 'field',
            'required_field': 1,
            'optional_field': 2,
        },
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
            'items_alias': 'Cannot decode "invalid integer" to integer',
            'non_field_error': 'Missing fields: "name"',
        }
    }

    # Act
    response = api_client.post('/with-request-data/', json=data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == expected_data


def test_without_argument():
    def method(argument: int):  # pragma: no cover
        return argument

    annotation_decorator = request_body('invalid_argument')

    with pytest.raises(AssertionError) as exception:
        annotation_decorator(method)
    assert exception.value.args == ('Not found argument "invalid_argument" in "method"',)


def test_unacceptible_content_type(api_client):
    response = api_client.post('/with-request-data/', content=b'hi', headers={'content-type': 'some/unknown'})

    assert response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    assert response.json() == {
        'status': 415,
        'type': 'urn:problem-type:unsupported-media-type',
        'title': 'Unsupported media type',
        'detail': '',
    }


def test_invalid_json(api_client):
    response = api_client.post('/with-request-data/', content=b'hi', headers={'content-type': 'application/json'})

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'status': 400,
        'type': 'urn:problem-type:request-data-decode',
        'title': 'Request data decode',
        'detail': 'Failed to decode request data',
        'errors': {'error': 'Invalid JSON: Expecting value: line 1 column 1 (char 0)'},
    }
