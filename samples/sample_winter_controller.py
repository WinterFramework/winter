from typing import Dict
from typing import List

import winter
from pydantic.dataclasses import dataclass
from rest_framework import serializers
from rest_framework import status


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

    @winter.route_get('hello')
    @winter.query_parameter('name', map_to='names')
    def hello(self, names: List[str] = None) -> str:
        names = ', '.join(names or ['stranger'])
        return f'Hello, {names}!'

    @winter.route_get('foo/{number}')
    @winter.query_parameter('name')
    def hello_with_response_code(self, name: str, number: int) -> winter.ResponseEntity:
        """
        :param name: Just a name
        :param number: Just a number
        """
        return winter.ResponseEntity(f'Hello, {name}! {number}', status.HTTP_201_CREATED)

    @winter.route_get('example')
    @winter.query_parameter('name')
    def second_hello(self, name: str) -> Greeting:
        return Greeting('Welcome', name)

    @winter.route_post('example2')
    @winter.input_serializer(GreetingSerializer, 'greeting')
    @winter.output_serializer(GreetingSerializer)
    def third_hello(self, greeting: Dict) -> Dict:
        return greeting
