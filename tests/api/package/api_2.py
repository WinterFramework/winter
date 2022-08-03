import winter
from .api_1 import API1


@winter.route('api_2/')
class API2:
    @winter.route_get('')
    def method_1(self) -> int:  # pragma: no cover
        return API1().method_1()

    @winter.route_get('')
    def method_2(self) -> int:  # pragma: no cover
        return 2
