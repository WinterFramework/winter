from http import HTTPStatus

import pytest


@pytest.mark.parametrize(['params', 'expected_body'], (
    ({'name': 'Winter'}, 'Hello, Winter!'),
    ({'name': 'Stranger'}, 'Hello, Stranger!'),
    ({}, 'Hello, stranger!'),
))
def test_simple_api(api_client, params, expected_body):
    response = api_client.get('/winter-simple/', params=params)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_body


def test_get_response_entity(api_client):
    response = api_client.get('/winter-simple/get-response-entity/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'number': 123,
    }


@pytest.mark.parametrize(('limit', 'offset', 'expected_previous', 'expected_next'), (
    (1, 1, '/winter-simple/page-response/?limit=1', '/winter-simple/page-response/?limit=1&offset=2'),
    (None, None, None, None),
    (2, 3, '/winter-simple/page-response/?limit=2&offset=1', '/winter-simple/page-response/?limit=2&offset=5'),
    (9, 3, '/winter-simple/page-response/?limit=9', None),
))
def test_page_response(api_client, limit, offset, expected_previous, expected_next):
    url = f'/winter-simple/page-response/?'
    query_params = []
    if limit is not None:
        query_params.append(f'limit={limit}')
    if offset is not None:
        query_params.append(f'offset={offset}')
    url += '&'.join(query_params)

    expected_body = {
        'objects': [{'number': 1}],
        'meta': {
            'limit': limit,
            'offset': offset,
            'next': expected_next,
            'previous': expected_previous,
            'total_count': 10,
        },
    }

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == HTTPStatus.OK, response.content
    assert response.json() == expected_body


def test_custom_page_response(api_client):
    expected_body = {
        'objects': [1, 2],
        'meta': {
            'limit': 2,
            'offset': 2,
            'next': '/winter-simple/custom-page-response/?limit=2&offset=4',
            'previous': '/winter-simple/custom-page-response/?limit=2',
            'total_count': 10,
            'extra': 456,
        },
    }
    request_data = {
        'limit': 2,
        'offset': 2,
    }

    # Act
    response = api_client.get('/winter-simple/custom-page-response/', params=request_data)

    # Assert
    assert response.status_code == HTTPStatus.OK, response.content
    assert response.json() == expected_body


def test_return_response(api_client):
    response = api_client.get('/winter-simple/return-response/')
    assert response.status_code == HTTPStatus.OK
    assert response.content == b'hi'


@pytest.mark.parametrize(('method', 'http_response_status'), (
    ('get', HTTPStatus.OK),
    ('post', HTTPStatus.OK),
    ('patch', HTTPStatus.OK),
    ('delete', HTTPStatus.NO_CONTENT),
    ('put', HTTPStatus.OK),
))
def test_methods(api_client, method, http_response_status):
    url = f'/winter-simple/{method}/'
    response = getattr(api_client, method)(url)
    assert response.status_code == http_response_status


def test_none_response(api_client):
    url = f'/winter-simple/get/'
    response = api_client.get(url)
    assert response.content == b''


def test_custom_query_parameters(api_client):
    url = '/winter-simple/custom-query-parameters/?x=1&x=2&y=3,4'
    response = api_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [1, 2, 3, 4]
