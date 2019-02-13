from typing import Dict

import pytest
from drf_yasg import openapi

from winter.controller import ControllerMethod
from winter.controller import get_controller_component
from winter.schema.generation import build_responses_schemas
from ..controllers import ControllerWithExceptions

controller_component = get_controller_component(ControllerWithExceptions)


@pytest.mark.parametrize('controller_method, expected_responses', [
    (controller_component.get_method('declared_and_thrown'), {
        '200': openapi.Schema(type=openapi.TYPE_STRING),
        '400': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING),
        }),
    }),
    (controller_component.get_method('not_declared_but_thrown'), {
        '200': openapi.Schema(type=openapi.TYPE_STRING),
    }),
    (controller_component.get_method('declared_but_no_handler'), {
        '200': openapi.Schema(type=openapi.TYPE_STRING),
    }),
])
def test_response_schema(controller_method: ControllerMethod, expected_responses: Dict):
    # Act
    responses = build_responses_schemas(controller_method)

    # Assert
    assert responses == expected_responses
