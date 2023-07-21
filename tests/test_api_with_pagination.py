from http import HTTPStatus
import pytest


def test_api_with_limits_redirects_to_default_limit(api_client):
    response = api_client.get('/paginated/with-limits/')

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers['Location'] == '/paginated/with-limits/?limit=20'


def test_api_with_limits_does_not_redirect_if_limit_is_set(api_client):
    response = api_client.get('/paginated/with-limits/?limit=30')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'limit': 30, 'offset': None}


def test_api_with_limits_fails_if_maximum_limit_is_exceeded(api_client):
    response = api_client.get('/paginated/with-limits/?limit=120')

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'status': 400,
        'detail': 'Maximum limit value is exceeded: 100',
        'title': 'Maximum limit value exceeded',
        'type': 'urn:problem-type:maximum-limit-value-exceeded',
    }


@pytest.mark.parametrize(
    ('query_string', 'expected_limit', 'expected_offset', 'expected_sort'), (
        ('limit=1&offset=3', 1, 3, 'name'),
        ('limit=1', 1, None, 'name'),
        ('limit=', None, None, 'name'),
        ('limit=0', None, None, 'name'),
        ('offset=3', None, 3, 'name'),
        ('', None, None, 'name'),
        ('offset=0', None, 0, 'name'),
        ('limit=10&offset=20&order_by=-id,name', 10, 20, '-id,name'),
        ('order_by=', None, None, 'name'),
    ),
)
def test_paginated_api(api_client, query_string, expected_limit, expected_offset, expected_sort):
    response = api_client.get('/paginated/?' + query_string)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        'limit': expected_limit,
        'offset': expected_offset,
        'sort': expected_sort,
    }


@pytest.mark.parametrize(
    ('query_string', 'message', 'errors_dict'), (
        ('limit=none', 'Failed to decode request data', {'error': 'Cannot decode "none" to PositiveInteger'}),
        ('offset=-20', 'Failed to decode request data', {'error': 'Cannot decode "-20" to PositiveInteger'}),
        ('order_by=id,', 'Invalid field for order: ""', {'error': 'Invalid field for order: ""'}),
        ('order_by=-', 'Invalid field for order: "-"', {'error': 'Invalid field for order: "-"'}),
        (
            'order_by=not_allowed_order_by_field',
            'Fields do not allowed as order by fields: "not_allowed_order_by_field"',
            {'error': 'Fields do not allowed as order by fields: "not_allowed_order_by_field"'},
        ),
    ),
)
def test_invalid_pagination(api_client, query_string, message, errors_dict):
    response = api_client.get('/paginated/?' + query_string)

    assert response.status_code == 400
    assert response.json() == {
        'status': 400,
        'type': 'urn:problem-type:request-data-decode',
        'title': 'Request data decode',
        'detail': 'Failed to decode request data',
        'errors': errors_dict,
    }
