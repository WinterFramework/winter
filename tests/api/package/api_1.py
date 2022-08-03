import winter


@winter.route('api_1/')
class API1:
    @winter.route_get('')
    def method_1(self) -> int:  # pragma: no cover
        return 1
