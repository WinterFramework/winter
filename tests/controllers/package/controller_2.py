import winter
from .controller_1 import Controller1


@winter.route('controller_2/')
class Controller2:
    @winter.route_get('')
    def method_1(self) -> int:  # pragma: no cover
        return Controller1().method_1()

    @winter.route_get('')
    def method_2(self) -> int:  # pragma: no cover
        return 2
