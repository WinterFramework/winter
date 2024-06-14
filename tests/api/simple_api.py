import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import List

from django.http import HttpRequest
from django.http import HttpResponse

import winter
from winter import ResponseEntity
from winter.core.json import JSONEncoder
from winter.data.pagination import Page
from winter.data.pagination import PagePosition


@dataclass
class Dataclass:
    number: int


@dataclass(frozen=True)
class CustomPage(Page[int]):
    extra: int


@dataclass
class CustomQueryParameters:
    x: List[int]
    y: List[int]


@winter.route('winter-simple/')
class SimpleAPI:

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
    def return_response(self) -> HttpResponse:
        return HttpResponse(b'hi')

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
    def no_route(self):  # pragma: no cover
        pass

    @winter.route_get('custom-query-parameters/{?x*,y}')
    @winter.web.query_parameters('query_parameters')
    def custom_query_parameters(self, query_parameters: CustomQueryParameters) -> List[int]:
        return [*query_parameters.x, *query_parameters.y]
