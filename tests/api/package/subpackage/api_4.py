from http import HTTPStatus

import winter.web


@winter.web.route('api_4/')
class API4:
    @winter.web.response_status(HTTPStatus.OK)
    def no_route(self):  # pragma: no cover
        pass
