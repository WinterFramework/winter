import winter


@winter.route('controller_1/')
class Controller1:
    @winter.route_get('')
    def method_1(self) -> int:  # pragma: no cover
        return 1
