from uuid import UUID

import winter
from winter import ResponseHeader


@winter.controller
@winter.route('with-response-headers/')
class ControllerWithResponseHeaders:

    @winter.response_header('x-header', 'header')
    @winter.route_get('str-header/')
    def str_header(self, header: ResponseHeader[str]) -> str:
        header.set('test header')
        return 'OK'

    @winter.response_header('x-header', 'header')
    @winter.route_get('int-header/')
    def int_header(self, header: ResponseHeader[int]) -> str:
        header.set(123)
        return 'OK'

    @winter.response_header('x-header', 'header')
    @winter.route_get('uuid-header/{?uid}')
    def uuid_header(self, uid: UUID, header: ResponseHeader[UUID]) -> str:
        header.set(uid)
        return 'OK'
