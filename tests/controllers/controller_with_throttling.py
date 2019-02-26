import winter.http
import winter

@winter.http.throttling('5/s')
@winter.route_get('with-throttling/')
class ControllerWithThrottlingOnController:

    @winter.route_get()

    def simple_method(self):
        return 1


@winter.route_get('with-throttling-on-method/')
class ControllerWithThrottlingOnMethod:

    @winter.route_get()
    @winter.http.throttling('5/s')
    def simple_method(self):
        return 1
