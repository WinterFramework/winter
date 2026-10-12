from typing import Tuple

import winter.web


class APIWithRequestHeaders:
    @winter.web.request_header('X-Header', to='header')
    @winter.web.route_post('with-request-header/')
    def method(self, header: int) -> int:
        return header

    @winter.web.request_header('X-Header', to='header')
    @winter.web.request_header('Y-Header', to='another_header')
    @winter.web.route_post('with-request-several-headers/')
    def method_with_several_headers(self, header: int, another_header: str) -> Tuple[int, str]:
        return header, another_header
