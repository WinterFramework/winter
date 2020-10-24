import datetime
from http import HTTPStatus

import freezegun
import pytest
from rest_framework.test import APIClient

from .entities import AuthorizedUser


@pytest.mark.parametrize('need_auth', (True, False))
def test_throttling(need_auth):
    now = datetime.datetime.now()
    duration = datetime.timedelta(milliseconds=150)
    client = APIClient()
    if need_auth:
        user = AuthorizedUser()
        client.force_authenticate(user)

    for i in range(1, 16):
        with freezegun.freeze_time(now):
            response = client.get('/with-throttling/')
            response_from_post = client.post('/with-throttling/')
            response_of_same = client.get('/with-throttling/same/')
            response_custom_exception = client.get('/with-throttling/custom-handler/')

            if 5 < i < 8 or 13 <= i < 15:
                assert response.status_code == response_of_same.status_code == response_custom_exception.status_code \
                       == HTTPStatus.TOO_MANY_REQUESTS, i
                expected_response = {
                    'status': 429,
                    'detail': 'Request was throttled',
                    'title': 'Throttle',
                    'type': 'urn:problem-type:throttle',
                }
                assert response.json() == response_of_same.json() == expected_response, i
                assert response_custom_exception.json() == 'custom throttle exception', i
            else:
                assert response.status_code == response_of_same.status_code == response_custom_exception.status_code \
                       == HTTPStatus.OK, i

            assert response_from_post.status_code == HTTPStatus.OK

        now += duration


def test_throttling_without_throttling():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    for i in range(1, 10):
        client_method = getattr(client, 'get')
        response = client_method('/with-throttling/without-throttling/')
        assert response.status_code == HTTPStatus.OK, i
