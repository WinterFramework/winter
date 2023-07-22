from http import HTTPStatus
from typing import List

from dataclasses import dataclass

import winter


@dataclass
class GreetingRequest:
    name: str


class TestRepository:
    def get_by_id(self, id_: int):
        return 123


@dataclass
class Greeting:
    message: str
    name: str


@winter.route('winter_sample/')
class SampleWinterAPI:

    def __init__(self, test_repository: TestRepository):
        self._test_repository = test_repository

    @winter.route_get('hello{?name}')
    @winter.map_query_parameter('name', to='names')
    def hello(self, names: List[str] = None) -> str:
        names = ', '.join(names or ['stranger'])
        return f'Hello, {names}!'

    @winter.route_get('foo/{number}{?name}')
    def hello_with_response_code(self, name: str, number: int) -> winter.ResponseEntity[str]:
        """
        :param name: Just a name
        :param number: Just a number
        """
        return winter.ResponseEntity[str](f'Hello, {name}! {number}', HTTPStatus.CREATED)

    @winter.route_get('example{?name}')
    def second_hello(self, name: str) -> Greeting:
        return Greeting('Welcome', name)

    @winter.route_post('example2')
    @winter.request_body('greeting')
    def third_hello(self, greeting: GreetingRequest) -> Greeting:
        return Greeting(message='got it', name=greeting.name)
