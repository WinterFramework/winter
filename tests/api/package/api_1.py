import winter.web


@winter.web.route('api_1/')
class API1:
    @winter.web.route_get('')
    def method_1(self) -> int:  # pragma: no cover
        return 1
