from http import HTTPStatus

from django.http import HttpRequest

import winter.web
from winter.web import Request
from winter.web import Response
from winter.web.output_processor import IOutputProcessor
from winter.web.output_processor import register_output_processor


class PlainTextProcessor(IOutputProcessor):
    def process_output(self, output, request: Request) -> Response:
        return Response(status_code=HTTPStatus.OK, body=str(output).encode(), headers={'content-type': 'text/plain'})


def _plain_text(func):
    return register_output_processor(func, PlainTextProcessor())


@winter.web.route('with-response/')
class APIWithResponse:

    @winter.web.route_get('raw/')
    def raw(self) -> Response:
        return Response(status_code=HTTPStatus.ACCEPTED, body=b'raw bytes', headers={'content-type': 'text/plain'})

    @winter.web.route_get('processed/')
    @_plain_text
    def processed(self) -> int:
        return 42

    @winter.web.route_get('request-info/')
    def request_info(self, request: Request, django_request: HttpRequest) -> dict:
        return {
            'method': request.method,
            'path': request.path,
            'full_path': request.full_path,
            'remote_address': request.remote_address,
            'same_django_request': request.django_request is django_request,
        }
