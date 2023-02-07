import winter


class APIWithRequestHeaders:
    @winter.request_header('X-Header', to='header')
    @winter.route_post('with-request-header/')
    def method(self, header: int) -> int:
        return header
