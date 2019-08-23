import winter


@winter.controller
@winter.route('with-response-headers/')
class ControllerWithResponseHeaders:

    @winter.response_header('x-header1', 'header1')
    @winter.route_post('one-header')
    def method(self, header1: str) -> str:
        """
        :param header1: Response Header 1
        """
        return 'OK'
