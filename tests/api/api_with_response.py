from http import HTTPStatus

from django.http import HttpRequest

import winter.web
from winter.web import Request
from winter.web import Response


@winter.web.route('with-response/')
class APIWithResponse:

    @winter.web.route_get('raw/')
    def raw(self) -> Response:
        return Response(status_code=HTTPStatus.ACCEPTED, body=b'raw bytes', headers={'content-type': 'text/plain'})

    @winter.web.route_get('request-info/')
    def request_info(self, request: Request, django_request: HttpRequest) -> dict:
        return {
            'method': request.method,
            'path': request.path,
            'full_path': request.full_path,
            'remote_address': request.remote_address,
            'same_django_request': request.django_request is django_request,
        }
