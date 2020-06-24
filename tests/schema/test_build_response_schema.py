import pytest
from rest_framework import serializers

import winter.core
import winter_django
from winter_openapi.generation import CanNotInspectReturnType
from winter_openapi.generation import build_response_schema


class UserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)


class Controller:

    @winter_django.output_serializer(UserSerializer)
    def with_output_serializer(self):
        pass

    @winter.core.component_method
    def with_invalid_return_type(self) -> object:
        pass


def test_with_output_serializer():
    schema = build_response_schema(Controller.with_output_serializer)

    assert isinstance(schema, UserSerializer)


def test_with_invalid_return_type():

    with pytest.raises(CanNotInspectReturnType) as e:
        build_response_schema(Controller.with_invalid_return_type)

    assert repr(e.value) == (
        'CanNotInspectReturnType(tests.schema.test_build_response_schema.Controller.with_invalid_return_type: '
        "-> <class 'object'>: Unknown type: <class 'object'>)"
    )
