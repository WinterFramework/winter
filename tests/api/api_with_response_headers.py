import datetime

import winter.web
from winter.web import ResponseHeader


@winter.web.route('with-response-headers/')
class APIWithResponseHeaders:

    @winter.web.response_header('x-header', 'header')
    @winter.web.route_get('str-header/')
    def str_header(self, header: ResponseHeader[str]) -> str:
        header.set('test header')
        return 'OK'

    @winter.web.response_header('x-header', 'header')
    @winter.web.route_get('int-header/')
    def int_header(self, header: ResponseHeader[int]) -> str:
        header.set(123)
        return 'OK'

    @winter.web.response_header('x-header', 'header')
    @winter.web.route_get('datetime-header/')
    def datetime_header(self, header: ResponseHeader[datetime.datetime]) -> str:
        novosibirsk = datetime.timezone(datetime.timedelta(hours=7))
        header.set(datetime.datetime(2026, 10, 27, 16, 54, 30, 123456, tzinfo=novosibirsk))
        return 'OK'

    @winter.web.response_header('x-header1', 'header1')
    @winter.web.response_header('x-header2', 'header2')
    @winter.web.route_get('two-headers/')
    def two_headers(self, header1: ResponseHeader[str], header2: ResponseHeader[str]) -> str:
        header1.set('header1')
        header2.set('header2')
        return 'OK'
