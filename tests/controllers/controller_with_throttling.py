import winter.drf


@winter.route_get('with-throttling/')
@winter.drf.no_authentication
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
