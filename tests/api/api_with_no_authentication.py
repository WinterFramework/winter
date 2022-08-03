import winter.web


@winter.route('winter-no-auth')
@winter.web.no_authentication
class APIWithNoAuthentication:

    @winter.route_get('/{?name}')
    def hello(self) -> str:
        return f'Hello, World!'
