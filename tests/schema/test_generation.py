import dataclasses
import pytest
from drf_yasg import openapi

import winter
from winter.routing import get_route
from winter.schema.generation import build_response_schema


@dataclasses.dataclass
class SimpleDataclass:
    number: int
    string: str


@pytest.mark.parametrize('return_type', (
    str,
    None,
    SimpleDataclass,
    object,
))
def test_build_response_schema(return_type):
    @winter.route('')
    class SimpleController:

        @winter.route_get('/simple/')
        def simple_method(self) -> return_type:
            return None

    route = get_route(SimpleController.simple_method)

    # Act
    schema = build_response_schema(route)

    # Assert
    assert isinstance(schema, openapi.SwaggerDict)
