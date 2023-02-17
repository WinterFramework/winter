import winter


@winter.web.no_authentication
class API2:
    @winter.route_patch('exception/')
    def update(self):  # pragma: no cover
        pass
