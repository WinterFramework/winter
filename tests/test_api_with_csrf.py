from http import HTTPStatus

from rest_framework.test import APIClient


def test_api_with_csrf_exempt_with_user_in_request():
    client = APIClient(enforce_csrf_checks=True)

    response = client.post('/api_with_csrf_exempt/', headers={'ADD_GUEST_USER_TO_REQUEST': ''})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'With CSRF exempt OK'


def test_api_with_csrf_exempt_without_user_in_request():
    client = APIClient(enforce_csrf_checks=True)

    response = client.post('/api_with_csrf_exempt/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'With CSRF exempt OK'


def test_api_without_csrf_exempt_with_user_in_request():
    client = APIClient(enforce_csrf_checks=True)

    response = client.post('/api_without_csrf_exempt/', headers={'ADD_GUEST_USER_TO_REQUEST': ''})

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'CSRF Failed: CSRF cookie not set.'}


def test_api_without_csrf_exempt_without_user_in_request():
    client = APIClient(enforce_csrf_checks=True)

    response = client.post('/api_without_csrf_exempt/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'With no CSRF exempt OK'
