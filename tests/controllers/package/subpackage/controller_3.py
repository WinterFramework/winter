import winter


@winter.route('controller_3/')
class Controller3:
    @winter.route_get('')
    def method_4(self) -> int:  # pragma: no cover
        return 4
