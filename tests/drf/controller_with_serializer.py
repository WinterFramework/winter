import dataclasses
from rest_framework import serializers

import winter.drf
from winter.drf import BodyWithContext


@dataclasses.dataclass
class SimpleDTO:
    number: int


class SimpleSerializer(serializers.Serializer):
    number = serializers.IntegerField()


class SerializerWithContext(serializers.Serializer):
    number = serializers.SerializerMethodField()

    def get_number(self, data) -> int:
        return self.context['additional_data']


@winter.controller
@winter.route('with-serializer')
class ControllerWithSerializer:

    @winter.route_post('/')
    @winter.drf.input_serializer(SimpleSerializer, argument_name='input_data')
    @winter.drf.output_serializer(SimpleSerializer)
    def post(self, input_data: dict) -> SimpleDTO:
        return SimpleDTO(input_data['number'] + 1)

    @winter.route_get('/with-context/')
    @winter.drf.output_serializer(SerializerWithContext)
    def post_back_with_context(self) -> BodyWithContext:
        return BodyWithContext({}, {'additional_data': 123})
