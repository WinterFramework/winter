import winter


@winter.route('api_with_csrf_exempt/')
@winter.web.no_authentication
class APIWithCsrfExempt:

    @winter.web.csrf_exempt
    @winter.route_post('')
    def method(self) -> str:
        return 'With CSRF exempt OK'


@winter.route('api_without_csrf_exempt/')
@winter.web.no_authentication
class APIWithoutCsrfExempt:

    @winter.route_post('')
    def method(self) -> str:
        return 'With no CSRF exempt OK'
