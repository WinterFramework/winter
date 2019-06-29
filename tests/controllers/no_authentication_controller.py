import winter


@winter.controller
@winter.route('winter-no-auth')
@winter.no_authentication
class NoAuthenticationController:

    @winter.route_get('/{?name}')
    def hello(self) -> str:
        return f'Hello, World!'
