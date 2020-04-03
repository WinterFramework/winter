import datetime
from uuid import UUID

import pytz

import winter
from winter.web import ResponseHeader


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
    @winter.route_get('datetime-isoformat-header/{?now}')
    def datetime_isoformat_header(self, now: float, header: ResponseHeader[datetime.datetime]) -> str:
        header.set(datetime.datetime.fromtimestamp(now))
        return 'OK'

    @winter.response_header('Last-Modified', 'header')
    @winter.route_get('last-modified-header/{?now}')
    def last_modified_header(self, now: float, header: ResponseHeader[datetime.datetime]) -> str:
        header.set(datetime.datetime.fromtimestamp(now).astimezone(pytz.timezone('Asia/Novosibirsk')))
        return 'OK'

    @winter.response_header('x-header', 'header')
    @winter.route_get('uuid-header/{?uid}')
    def uuid_header(self, uid: UUID, header: ResponseHeader[UUID]) -> str:
        header.set(uid)
        return 'OK'

    @winter.response_header('x-header1', 'header1')
    @winter.response_header('x-header2', 'header2')
    @winter.route_get('two-headers/')
    def two_headers(self, header1: ResponseHeader[str], header2: ResponseHeader[str]) -> str:
        header1.set('header1')
        header2.set('header2')
        return 'OK'

    @winter.route_get('header-without-annotation/')
    def header_without_annotation(self, header: ResponseHeader[str]) -> str:
        return 'OK'
