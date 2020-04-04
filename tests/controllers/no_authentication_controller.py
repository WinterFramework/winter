import winter.drf


@winter.controller
@winter.route('winter-no-auth')
@winter.drf.no_authentication
class NoAuthenticationController:

    @winter.route_get('/{?name}')
    def hello(self) -> str:
        return f'Hello, World!'
