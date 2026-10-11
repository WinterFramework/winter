import winter.web


@winter.web.route('api_3/')
class API3:
    @winter.web.route_get('')
    def method_4(self) -> int:  # pragma: no cover
        return 4
