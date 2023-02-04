from http import HTTPStatus

import winter


@winter.route('api_4/')
class API4:
    @winter.response_status(HTTPStatus.OK)
    def no_route(self):  # pragma: no cover
        pass
