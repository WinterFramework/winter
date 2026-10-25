
import winter.web
from winter.web import route_post, route_get
from winter.web import Request
from winter.web.throttling import reset


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

    @route_get('without-user/')
    @winter.web.throttling('5/s')
    def method_for_request_without_user(self) -> int:
        return 1

    @route_get('with-reset/{?is_reset}')
    @winter.web.throttling('5/s', 'reset_scope')
    def simple_method_with_reset(self, request: Request, is_reset: bool) -> int:
        if is_reset:
            reset(request, 'reset_scope')
        return 1
