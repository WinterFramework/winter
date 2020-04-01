from typing import Dict
from typing import List

from dataclasses import dataclass
from rest_framework import serializers
from rest_framework import status

import winter


class GreetingSerializer(serializers.Serializer):
    name = serializers.CharField()


class TestRepository:
    def get_by_id(self, id_: int):
        return 123


@dataclass
class Greeting:
    message: str
    name: str


@winter.controller
@winter.route('winter_sample/')
class SampleWinterController:

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
        return winter.ResponseEntity[str](f'Hello, {name}! {number}', status.HTTP_201_CREATED)

    @winter.route_get('example{?name}')
    def second_hello(self, name: str) -> Greeting:
        return Greeting('Welcome', name)

    @winter.route_post('example2')
    @winter.input_serializer(GreetingSerializer, 'greeting')
    @winter.output_serializer(GreetingSerializer)
    def third_hello(self, greeting: Dict) -> Dict:
        return greeting
