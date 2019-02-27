import winter.http
import winter

@winter.http.throttling('5/s')
@winter.route_get('with-throttling-on-controller/')
class ControllerWithThrottlingOnController:

    @winter.route_get()
    def simple_method(self):
        return 1

    @winter.http.throttling(None)
    @winter.route_post()
    def method_without_throttling(self):
        return None


@winter.route_get('with-throttling-on-method/')
class ControllerWithThrottlingOnMethod:

    @winter.route_get()
    @winter.http.throttling('5/s')
    def simple_method(self):
        return 1

    @winter.route_get('without-throttling/')
    def method_without_throttling(self):
        return None