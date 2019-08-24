import winter
from winter import ResponseHeader


@winter.controller
@winter.route('with-response-headers/')
class ControllerWithResponseHeaders:

    @winter.response_header('x-header1', 'header1')
    @winter.route_get('one-header/')
    def method(self, header1: ResponseHeader[str]) -> str:
        return 'OK'
