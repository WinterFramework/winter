import winter


@winter.controller
@winter.route('controller_with_path_parameters/{param1}/')
class ControllerWithPathParameters:

    @winter.route_get('{param2}/')
    @winter.query_parameter('param3')
    def test(self, param1: str, param2: int, param3: str) -> str:
        return 'Hello, sir!'
