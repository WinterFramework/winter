from http import HTTPStatus

from django.http import HttpRequest

import winter.web
from winter.web import route_post, route_get, raises, response_status, ExceptionHandler
from winter.web.exceptions import ThrottleException
from winter.web.throttling import reset


class CustomThrottleExceptionHandler(ExceptionHandler):
    @response_status(HTTPStatus.TOO_MANY_REQUESTS)
    def handle(self, exception: ThrottleException) -> str:
        return 'custom throttle exception'


@route_get('with-throttling/')
class APIWithThrottling:

    @route_get()
    @winter.web.throttling('5/s')
    def simple_method(self) -> int:
        return 1

    @route_post()
    def simple_post_method(self) -> int:
        return 1

    @route_get('same/')
    @winter.web.throttling('5/s')
    def same_simple_method(self) -> int:
        return 1

    @route_get('without-throttling/')
    def method_without_throttling(self):
        pass

    @route_get('custom-handler/')
    @winter.web.throttling('5/s')
    @raises(ThrottleException, CustomThrottleExceptionHandler)
    def simple_method_with_custom_handler(self) -> int:
        return 1

    @route_get('with-reset/{?is_reset}')
    @winter.web.throttling('5/s', 'reset_scope')
    def simple_method_with_reset(self, request: HttpRequest, is_reset: bool) -> int:
        if is_reset:
            reset(request, 'reset_scope')
        return 1
