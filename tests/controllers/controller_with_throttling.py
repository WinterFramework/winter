from http import HTTPStatus

import winter.web
from winter.web import ExceptionHandler
from winter.web.exceptions import ThrottleException


class CustomThrottleExceptionHandler(ExceptionHandler):
    @winter.response_status(HTTPStatus.TOO_MANY_REQUESTS)
    def handle(self, exception: ThrottleException) -> str:
        return 'custom throttle exception'


@winter.route_get('with-throttling/')
@winter.web.no_authentication
class ControllerWithThrottling:

    @winter.route_get()
    @winter.web.throttling('5/s')
    def simple_method(self) -> int:
        return 1

    @winter.route_post()
    def simple_post_method(self) -> int:
        return 1

    @winter.route_get('same/')
    @winter.web.throttling('5/s')
    def same_simple_method(self) -> int:
        return 1

    @winter.route_get('without-throttling/')
    def method_without_throttling(self):
        pass

    @winter.route_get('custom-handler/')
    @winter.web.throttling('5/s')
    @winter.raises(ThrottleException, CustomThrottleExceptionHandler)
    def simple_method_with_custom_handler(self) -> int:
        return 1
