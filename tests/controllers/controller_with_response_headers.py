import winter


@winter.controller
@winter.route('with-response-headers/')
class ControllerWithResponseHeaders:

    @winter.response_header('x-header1', 'header1')
    @winter.route_get('one-header/')
    def method(self) -> str:
        return 'OK'
