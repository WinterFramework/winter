import winter.web


@winter.controller
@winter.route('winter-no-auth')
@winter.web.no_authentication
class NoAuthenticationController:

    @winter.route_get('/{?name}')
    def hello(self) -> str:
        return f'Hello, World!'
