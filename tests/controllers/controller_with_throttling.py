import winter.http
import winter


@winter.http.throttling('6/s', scope='ControllerWithThrottlingOnController')
@winter.no_authentication
@winter.route_get('with-throttling-on-controller/')
class ControllerWithThrottlingOnController:

    @winter.route_get()
    def simple_method(self):
        return 1

    @winter.route_get('same/')
    def same_simple_method(self):
        return 1

    @winter.http.throttling(None)
    @winter.route_post()
    def method_without_throttling(self):
        return None


@winter.route_get('with-throttling-on-method/')
@winter.no_authentication
class ControllerWithThrottlingOnMethod:

    @winter.route_get()
    @winter.http.throttling('5/s')
    def simple_method(self):
        return 1

    @winter.route_get('same/')
    @winter.http.throttling('5/s')
    def same_simple_method(self):
        return 1

    @winter.route_get('without-throttling/')
    def method_without_throttling(self):
        return None
