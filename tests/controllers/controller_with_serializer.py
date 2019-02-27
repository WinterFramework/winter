import dataclasses
from rest_framework import serializers

import winter


@dataclasses.dataclass
class SimpleDTO:
    number: int


class SimpleSerializer(serializers.Serializer):
    number = serializers.IntegerField()


@winter.controller
@winter.route('with-serializer')
class ControllerWithSerializer:

    @winter.route_post('/')
    @winter.input_serializer(SimpleSerializer, argument_name='input_data')
    @winter.output_serializer(SimpleSerializer)
    def simple_method(self, input_data: dict) -> SimpleDTO:
        return SimpleDTO(input_data['number'] + 1)
