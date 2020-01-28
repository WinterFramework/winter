import winter


@winter.route_get('with-throttling/')
@winter.no_authentication
class ControllerWithThrottling:

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
