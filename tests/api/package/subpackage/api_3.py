import winter


@winter.route('api_3/')
class API3:
    @winter.route_get('')
    def method_4(self) -> int:  # pragma: no cover
        return 4
