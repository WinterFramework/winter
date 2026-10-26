import injector
import pytest
from django.test import RequestFactory

import winter.django
import winter.web


@pytest.mark.parametrize(
    'hello_world_query, hello_world_header',
    [
        ('', None),
        ('?hello_world', 'Hello, World!'),
    ],
)
def test_interceptor_headers(api_client, hello_world_query, hello_world_header):
    url = f'/winter-simple/get/{hello_world_query}'
    response = api_client.get(url)
    assert response.headers.get('x-method') == 'SimpleAPI.get'
    assert response.headers.get('x-hello-world') == hello_world_header


class _Calls(list):
    pass


class _RecordingInterceptor(winter.web.Interceptor):
    @injector.inject
    def __init__(self, calls: _Calls):
        self._calls = calls

    def pre_handle(self):
        self._calls.append(type(self).__name__)


class _InterceptorA(_RecordingInterceptor):
    pass


class _InterceptorB(_RecordingInterceptor):
    pass


class _CallsAPI:
    @winter.web.route_get('calls/')
    def get(self, calls: _Calls):
        calls.append('API')


def test_interceptors_run_in_given_order_before_api_method():
    calls = _Calls()
    app = winter.web.WebApplication(
        modules=[],
        injector=injector.Injector([lambda binder: binder.bind(_Calls, to=calls)]),
        interceptors=[_InterceptorB, _InterceptorA],
    )
    app.add(_CallsAPI)
    [url] = winter.django.create_urls(app)

    # Act
    url.callback(RequestFactory().get('/calls/'))

    # Assert
    assert calls == ['_InterceptorB', '_InterceptorA', 'API']
