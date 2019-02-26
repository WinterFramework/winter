import winter.http
import winter

@winter.controller
@winter.route_get('with-throttling')
class ControllerWithThrottling:

    @winter.http.throttling(5, 60)
    @winter.route_get('/')
    def simple_method(self):
        return 1