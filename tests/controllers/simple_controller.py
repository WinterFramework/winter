from http import HTTPStatus

import dataclasses

import winter
from winter import ResponseEntity
from winter.pagination import Page
from winter.pagination import PagePosition


@dataclasses.dataclass
class Dataclass:
    number: int


@winter.controller
@winter.route('winter-simple/')
class SimpleController:

    @winter.query_parameter('name')
    @winter.route_get()
    def hello(self, name: str = 'stranger') -> str:
        return f'Hello, {name}!'

    @winter.route_get('page-response/')
    def page_response(self, page_position: PagePosition) -> Page[Dataclass]:
        items = [Dataclass(1)]
        return Page(10, items, page_position)

    @winter.route_get('get-response-entity/')
    @winter.response_status(HTTPStatus.ACCEPTED)
    def return_response_entity(self) -> ResponseEntity:
        return ResponseEntity(Dataclass(123), status_code=HTTPStatus.OK)
