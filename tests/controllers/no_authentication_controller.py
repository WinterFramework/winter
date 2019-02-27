import winter


@winter.controller
@winter.route('winter_no_auth')
@winter.no_authentication
class NoAuthenticationController:

    @winter.query_parameter('name')
    @winter.route_get('/')
    def hello(self) -> str:
        return f'Hello, World!'
