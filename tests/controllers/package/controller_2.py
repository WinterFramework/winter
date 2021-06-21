import winter


@winter.route('controller_2/')
class Controller2:
    @winter.route_get('')
    def method_1(self) -> int:
        return 1

    @winter.route_get('')
    def method_2(self) -> int:
        return
