import dataclasses

import winter
from winter.pagination import Page
from winter.pagination import PagePosition


@dataclasses.dataclass
class Dataclass:
    number: int


@winter.controller
@winter.route('winter_simple/')
class SimpleController:

    @winter.query_parameter('name')
    @winter.route_get()
    def hello(self, name: str = 'stranger') -> str:
        return f'Hello, {name}!'

    @winter.route_get('page-response/')
    def page_response(self, page_position: PagePosition) -> Page[Dataclass]:
        items = [Dataclass(1)]
        return Page(10, items, page_position)
