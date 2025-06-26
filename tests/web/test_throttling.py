import datetime
from http import HTTPStatus

import freezegun
import pytest
from mock import patch

from winter.web import RedisThrottlingConfiguration
from winter.web import ThrottlingMisconfigurationException
from winter.web import set_redis_throttling_configuration
from winter.web.throttling.redis_throttling_client import get_redis_throttling_client
from winter.web.throttling import redis_throttling_client
from winter.web.throttling import redis_throttling_configuration

expected_error_response = {
    'status': 429,
    'detail': 'Request was throttled',
    'title': 'Throttle',
    'type': 'urn:problem-type:throttle',
}


@pytest.mark.parametrize('endpoint_url, auth, expected_response', [
    ('/with-throttling/', '', expected_error_response),
    ('/with-throttling/same/', '', expected_error_response),
    ('/with-throttling/custom-handler/', 'user_none', 'custom throttle exception'),
    ('/with-throttling/', 'user', expected_error_response),
    ('/with-throttling/same/', 'user', expected_error_response),
    ('/with-throttling/custom-handler/', 'user', 'custom throttle exception'),
])
def test_get_throttling(api_client, endpoint_url, auth, expected_response):
    now = datetime.datetime.now()
    duration = datetime.timedelta(milliseconds=150)

    for i in range(1, 16):
        with freezegun.freeze_time(now):
            response = api_client.get(endpoint_url, headers={'Test-Authorize': auth})

            if 5 < i < 8 or 13 <= i < 15:
                assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS, i
                assert response.json() == expected_response, i
            else:
                assert response.status_code == HTTPStatus.OK, i

        now += duration


@pytest.mark.parametrize('need_auth', (True, False))
def test_post_without_throttling(api_client, need_auth):
    now = datetime.datetime.now()
    duration = datetime.timedelta(milliseconds=150)

    for i in range(1, 16):
        with freezegun.freeze_time(now):
            response = api_client.post('/with-throttling/', headers={'Test-Authorize': 'user'} if need_auth else {})
            assert response.status_code == HTTPStatus.OK

        now += duration


def test_throttling_without_throttling(api_client):
    for i in range(1, 16):
        response = api_client.get('/with-throttling/without-throttling/')
        assert response.status_code == HTTPStatus.OK, i


def test_get_throttling_with_conditional_reset(api_client):
    now = datetime.datetime.now()

    with freezegun.freeze_time(now):
        for i in range(1, 10):
            is_reset = True if i == 5 else False
            response = api_client.get(f'/with-throttling/with-reset/?is_reset={is_reset}')
            assert response.status_code == HTTPStatus.OK, i


@patch.object(redis_throttling_client, 'get_redis_throttling_configuration', return_value=None)
@patch.object(redis_throttling_client, '_redis_throttling_client', None)
def test_get_redis_throttling_client_without_configuration(_):
    with pytest.raises(ThrottlingMisconfigurationException) as exc_info:
        get_redis_throttling_client()

    assert 'Configuration for Redis must be set' in str(exc_info.value)


@patch.object(
    redis_throttling_configuration,
    '_redis_throttling_configuration',
    RedisThrottlingConfiguration(
        host='localhost',
        port=1234,
        db=0,
        password=None
    )
)
def test_try_to_set_redis_configuration_twice():
    configuration = RedisThrottlingConfiguration(
        host='localhost',
        port=5678,
        db=0,
        password=None
    )
    with pytest.raises(ThrottlingMisconfigurationException) as exc_info:
        set_redis_throttling_configuration(configuration)

    assert 'RedisThrottlingConfiguration is already initialized' in str(exc_info.value)
