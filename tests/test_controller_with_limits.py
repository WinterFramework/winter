from http import HTTPStatus

from rest_framework.test import APIClient

from tests.entities import AuthorizedUser


def test_controller_with_limits_redirects_to_default_limit():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    response = client.get('/with-limits/')

    assert response.status_code == HTTPStatus.FOUND
    assert response['Location'] == '/with-limits/?limit=20'


def test_controller_with_limits_does_not_redirect_if_limit_is_set():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    response = client.get('/with-limits/?limit=30')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'limit': 30, 'offset': None}


def test_controller_with_limits_fails_if_maximum_limit_is_exceeded():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    response = client.get('/with-limits/?limit=120')

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'status': 400,
        'detail': 'Maximum limit value is exceeded: 100',
        'title': 'Maximum limit value exceeded',
        'type': 'urn:problem-type:maximum-limit-value-exceeded',
    }
