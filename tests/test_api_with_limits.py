from http import HTTPStatus


def test_api_with_limits_redirects_to_default_limit(api_client):
    response = api_client.get('/with-limits/', headers={'Test-Authorize': 'user'})

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers['Location'] == '/with-limits/?limit=20'


def test_api_with_limits_does_not_redirect_if_limit_is_set(api_client):
    response = api_client.get('/with-limits/?limit=30', headers={'Test-Authorize': 'user'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'limit': 30, 'offset': None}


def test_api_with_limits_fails_if_maximum_limit_is_exceeded(api_client):
    response = api_client.get('/with-limits/?limit=120', headers={'Test-Authorize': 'user'})

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'status': 400,
        'detail': 'Maximum limit value is exceeded: 100',
        'title': 'Maximum limit value exceeded',
        'type': 'urn:problem-type:maximum-limit-value-exceeded',
    }
