from http import HTTPStatus

from django.http import HttpRequest

import winter.web
from winter.web import Request
from winter.web import Response
from winter.web.output_processor import IOutputProcessor
from winter.web.output_processor import register_output_processor


class PlainTextProcessor(IOutputProcessor):
    """Renders the method result as text/plain instead of JSON."""

    def process_output(self, output: str, request: Request) -> Response:
        return Response(status_code=HTTPStatus.OK, body=output.encode(), headers={'content-type': 'text/plain'})


def plain_text(func):
    """Same shape as winter.django.output_template, but with an adapter-independent processor."""
    return register_output_processor(func, PlainTextProcessor())


@winter.web.route('with-response/')
class APIWithResponse:

    @winter.web.route_get('raw/')
    def raw(self) -> Response:
        return Response(status_code=HTTPStatus.ACCEPTED, body=b'raw bytes', headers={'content-type': 'text/plain'})

    @winter.web.route_get('greeting/')
    @plain_text
    def greeting(self) -> str:
        return 'Hello, Winter'

    @winter.web.route_get('request-info/')
    def request_info(self, request: Request, django_request: HttpRequest) -> dict:
        return {
            'method': request.method,
            'path': request.path,
            'full_path': request.full_path,
            'remote_address': request.remote_address,
            'same_django_request': request.django_request is django_request,
        }
