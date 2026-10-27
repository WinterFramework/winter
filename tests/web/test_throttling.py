import datetime
from http import HTTPStatus

import freezegun
import pytest

import winter.django
import winter.web
from winter.web import ThrottlingMisconfigurationException
from winter.web.throttling import InMemoryThrottlingStorage
from winter.web.throttling import Throttle
from winter.web.throttling.throttling import Throttling

expected_error_response = {
    'status': 429,
    'detail': 'Request was throttled',
    'title': 'Throttle',
    'type': 'urn:problem-type:throttle',
}


@pytest.mark.parametrize('endpoint_url, auth, expected_response', [
    ('/with-throttling/', '', expected_error_response),
    ('/with-throttling/same/', '', expected_error_response),
    ('/with-throttling/without-user/', 'user_none', expected_error_response),
    ('/with-throttling/', 'user', expected_error_response),
    ('/with-throttling/same/', 'user', expected_error_response),
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


class _ThrottledAPI:
    @winter.web.route_get('throttled/')
    @winter.web.throttling('5/s')
    def get(self):  # pragma: no cover
        pass


def test_throttling_without_storage_in_injector_fails_startup():
    app = winter.web.WebApplication(modules=[])
    app.add(_ThrottledAPI)

    # Act
    with pytest.raises(ThrottlingMisconfigurationException) as exception_info:
        winter.django.create_urls(app)

    # Assert
    assert str(exception_info.value) == (
        '_ThrottledAPI.get: @throttling needs a ThrottlingStorage bound in the injector'
    )


class _NotThrottledAPI:
    @winter.web.route_get('not-throttled/')
    def get(self, throttle: Throttle):  # pragma: no cover
        pass


def test_throttle_argument_without_throttling_fails_startup():
    app = winter.web.WebApplication(modules=[])
    app.add(_NotThrottledAPI)

    # Act
    with pytest.raises(TypeError) as exception_info:
        winter.django.create_urls(app)

    # Assert
    assert str(exception_info.value) == (
        '_NotThrottledAPI.get: argument throttle (Throttle) '
        'is not mapped from the request and has no binding in the injector'
    )


def test_throttle_resets_identity_it_counted_the_request_for():
    storage = InMemoryThrottlingStorage()
    identities = iter(['10.0.0.1', '42'])
    throttling = Throttling(num_requests=1, duration=60, scope='login')
    throttle = Throttle(throttling, storage, None, lambda request: next(identities))
    throttle.allow_request()

    # Act
    throttle.reset()

    # Assert
    assert storage.is_request_allowed('throttle_login_10.0.0.1', duration=60, num_requests=1)


def test_in_memory_storage_sliding_window():
    throttling_storage = InMemoryThrottlingStorage()
    now = datetime.datetime.now()

    def at(seconds: float) -> bool:
        with freezegun.freeze_time(now + datetime.timedelta(seconds=seconds)):
            return throttling_storage.is_request_allowed('key', 10, 2)

    # two requests per 10 seconds; the third one inside the window is rejected and not counted
    assert [at(0), at(1), at(2), at(5)] == [True, True, False, False]
    with freezegun.freeze_time(now):
        assert throttling_storage.is_request_allowed('other key', 10, 2)

    # the requests made at 0 and 1 have left the window
    assert [at(11.5), at(12), at(12.5)] == [True, True, False]

    throttling_storage.delete('key')
    assert at(12.5)
