import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import List

from django.http import HttpRequest
from django.http import HttpResponse

import winter.web
from winter.web import ResponseEntity
from winter.json import JSONEncoder
from winter.pagination import Page
from winter.pagination import PagePosition


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


@winter.web.route('winter-simple/')
class SimpleAPI:

    @winter.web.route_get('{?name}')
    def hello(self, name: str = 'stranger') -> str:
        return f'Hello, {name}!'

    @winter.web.route_get('page-response/')
    def page_response(self, page_position: PagePosition) -> Page[Dataclass]:
        items = [Dataclass(1)]
        return Page(10, items, page_position)

    @winter.web.route_get('custom-page-response/')
    def custom_page_response(self, page_position: PagePosition) -> CustomPage:
        return CustomPage(total_count=10, items=[1, 2], position=page_position, extra=456)

    @winter.web.route_get('get-response-entity/')
    @winter.web.response_status(HTTPStatus.ACCEPTED)
    def return_response_entity(self) -> ResponseEntity[Dataclass]:
        return ResponseEntity[Dataclass](Dataclass(123), status_code=HTTPStatus.OK)

    @winter.web.route_get('return-response/')
    def return_response(self) -> HttpResponse:
        return HttpResponse(b'hi')

    @winter.web.route_get('get/')
    def get(self):
        pass

    @winter.web.route_post('post/')
    def post(self):
        pass

    @winter.web.route_delete('delete/')
    def delete(self):
        pass

    @winter.web.route_patch('patch/')
    def patch(self):
        pass

    @winter.web.route_put('put/')
    def put(self):
        pass

    @winter.web.response_status(HTTPStatus.OK)
    def no_route(self):  # pragma: no cover
        pass

    @winter.web.route_get('custom-query-parameters/{?x*,y}')
    @winter.web.query_parameters('query_parameters')
    def custom_query_parameters(self, query_parameters: CustomQueryParameters) -> List[int]:
        return [*query_parameters.x, *query_parameters.y]
