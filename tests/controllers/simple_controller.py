from http import HTTPStatus

from dataclasses import dataclass
from rest_framework.request import Request
from rest_framework.response import Response

import winter
from winter import ResponseEntity
from winter.data.pagination import Page
from winter.data.pagination import PagePosition


@dataclass
class Dataclass:
    number: int


@dataclass(frozen=True)
class CustomPage(Page[int]):
    extra: int


@winter.controller
@winter.route('winter-simple/')
class SimpleController:

    @winter.route_get('{?name}')
    def hello(self, name: str = 'stranger') -> str:
        return f'Hello, {name}!'

    @winter.route_get('page-response/')
    def page_response(self, page_position: PagePosition) -> Page[Dataclass]:
        items = [Dataclass(1)]
        return Page(10, items, page_position)

    @winter.route_get('custom-page-response/')
    def custom_page_response(self, page_position: PagePosition) -> CustomPage:
        return CustomPage(total_count=10, items=[1, 2], position=page_position, extra=456)

    @winter.route_get('get-response-entity/')
    @winter.response_status(HTTPStatus.ACCEPTED)
    def return_response_entity(self) -> ResponseEntity[Dataclass]:
        return ResponseEntity[Dataclass](Dataclass(123), status_code=HTTPStatus.OK)

    @winter.route_get('return-response/')
    def return_response(self, request: Request) -> Response:
        data = {'logged_in': bool(request.user)}
        return Response(data=data)

    @winter.route_get('get/')
    def get(self):
        pass

    @winter.route_post('post/')
    def post(self):
        pass

    @winter.route_delete('delete/')
    def delete(self):
        pass

    @winter.route_patch('patch/')
    def patch(self):
        pass

    @winter.route_put('put/')
    def put(self):
        pass

    @winter.response_status(HTTPStatus.OK)
    def no_route(self):
        pass
