from typing import Dict
from typing import Type

import pytest
from drf_yasg import openapi

import winter
from winter.controller import get_component
from winter.routing.routing import get_route
from winter.schema.generation import build_response_schema
from winter.schema.generation import build_responses_schemas
from ..controllers import ControllerWithExceptions


@pytest.mark.parametrize(('return_type', 'expected_response'), (
    (str, openapi.Schema(type=openapi.TYPE_STRING)),
    (None, openapi.Response(description='')),
    (object, openapi.Response(description='')),
))
def test_build_response_schema(return_type, expected_response):
    @winter.route('')
    class SimpleController:

        @winter.route_get('/simple/')
        def simple_method(self) -> return_type:
            return None

    # Act
    schema = build_response_schema(SimpleController.simple_method)

    # Assert
    assert isinstance(schema, openapi.SwaggerDict)


@pytest.mark.parametrize('controller_class, method_name, expected_responses', [
    (ControllerWithExceptions, 'declared_and_thrown', {
        '200': openapi.Schema(type=openapi.TYPE_STRING),
        '400': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING),
        }),
    }),
    (ControllerWithExceptions, 'with_custom_handler', {
        '200': openapi.Schema(type=openapi.TYPE_STRING),
        '401': openapi.Schema(type=openapi.TYPE_INTEGER),
    }),
    (ControllerWithExceptions, 'not_declared_but_thrown', {
        '200': openapi.Schema(type=openapi.TYPE_STRING),
    }),
    (ControllerWithExceptions, 'declared_but_no_handler', {
        '200': openapi.Schema(type=openapi.TYPE_STRING),
    }),
])
def test_response_schema(controller_class: Type, method_name: str, expected_responses: Dict):
    component = get_component(controller_class)
    method = component.get_method(method_name)
    route = get_route(method)

    # Act
    responses = build_responses_schemas(route)

    # Assert
    assert responses == expected_responses
