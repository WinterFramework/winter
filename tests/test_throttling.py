import datetime
from http import HTTPStatus

import freezegun
import pytest
from rest_framework.test import APIClient

from .entities import AuthorizedUser


expected_error_response = {
    'status': 429,
    'detail': 'Request was throttled',
    'title': 'Throttle',
    'type': 'urn:problem-type:throttle',
}


@pytest.mark.parametrize('endpoint_url, need_auth, expected_response', [
    ('/with-throttling/', False, expected_error_response),
    ('/with-throttling/same/', False, expected_error_response),
    ('/with-throttling/custom-handler/', False, 'custom throttle exception'),
    ('/with-throttling/', True, expected_error_response),
    ('/with-throttling/same/', True, expected_error_response),
    ('/with-throttling/custom-handler/', True, 'custom throttle exception'),

])
def test_get_throttling(endpoint_url, need_auth, expected_response):
    now = datetime.datetime.now()
    duration = datetime.timedelta(milliseconds=150)
    client = APIClient()
    if need_auth:
        user = AuthorizedUser()
        client.force_authenticate(user)

    for i in range(1, 16):
        with freezegun.freeze_time(now):
            response = client.get(endpoint_url)

            if 5 < i < 8 or 13 <= i < 15:
                assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS, i
                assert response.json() == expected_response, i
            else:
                assert response.status_code == HTTPStatus.OK, i

        now += duration


@pytest.mark.parametrize('need_auth', (True, False))
def test_post_without_throttling(need_auth):
    now = datetime.datetime.now()
    duration = datetime.timedelta(milliseconds=150)
    client = APIClient()
    if need_auth:
        user = AuthorizedUser()
        client.force_authenticate(user)

    for i in range(1, 16):
        with freezegun.freeze_time(now):
            response = client.post('/with-throttling/')
            assert response.status_code == HTTPStatus.OK

        now += duration


def test_throttling_without_throttling():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    for i in range(1, 16):
        response = client.get('/with-throttling/without-throttling/')
        assert response.status_code == HTTPStatus.OK, i


def test_get_throttling_with_conditional_reset():
    now = datetime.datetime.now()
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    with freezegun.freeze_time(now):
        for i in range(1, 10):
            is_reset = True if i == 5 else False
            response = client.get(f'/with-throttling/with-reset/?is_reset={is_reset}')
            assert response.status_code == HTTPStatus.OK, i
