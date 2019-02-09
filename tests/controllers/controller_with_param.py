import winter


@winter.controller
@winter.route('controller-with-param/{param}/')
class ControllerWithParam:

    @winter.route_get('return_str/')
    def return_str(self, param: str) -> dict:
        return {'param': param}

    @winter.route_get('return_int/')
    def return_int(self, param: int) -> dict:
        return {'param': param}
