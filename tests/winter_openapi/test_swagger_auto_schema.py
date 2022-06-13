import dataclasses
from typing import Optional

from drf_yasg import openapi
from rest_framework import serializers

import pytest
import winter
import winter_django
from winter_django.view import create_drf_view
from winter_openapi import SwaggerAutoSchema
from winter.web import MediaType
from winter.web.routing import get_route

from tests.controllers import ControllerWithExceptions
from tests.controllers import ControllerWithProblemExceptions


@dataclasses.dataclass
class NestedDTO:
    a: int
    b: str


@dataclasses.dataclass
class UserDTO:
    name: str
    nested_dto: NestedDTO
    surname: str = ''
    age: Optional[int] = None


class UserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)

    def to_internal_value(self, data):  # pragma: no cover
        data = super().to_internal_value(data)
        return UserDTO(**data)


class Controller:

    @winter.request_body(argument_name='request_body')
    @winter.route_post(
        '{path_param}/{?query_param,another_query_param}',
        produces=[MediaType.APPLICATION_JSON_UTF8],
        consumes=[MediaType.APPLICATION_JSON_UTF8],
    )
    def post(self, path_param: int, query_param: int, request_body: UserDTO) -> UserDTO:  # pragma: no cover
        """
        This is post method
        :param path_param:
        :param query_param:
        :param request_body:
        :return:
        """
        return request_body

    @winter_django.input_serializer(UserSerializer, argument_name='request_body')
    @winter.route_post('with-serializer/')
    def post_with_serializer(self, request_body: UserDTO) -> UserDTO:  # pragma: no cover
        return request_body

    @winter.route_get('without-body/')
    def get(self):  # pragma: no cover
        pass


user_dto_request_schema = openapi.Schema(
    'UserDTO',
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'nested_dto': {
            'type': openapi.TYPE_OBJECT,
            'title': 'NestedDTO',
            'properties': {
                'a': {'type': openapi.TYPE_INTEGER},
                'b': {'type': openapi.TYPE_STRING},
            },
            'required': ['a', 'b'],
        },
        'surname': openapi.Schema(type=openapi.TYPE_STRING),
        'age': openapi.Schema(type=openapi.TYPE_INTEGER, **{'x-nullable': True}),
    },
    required=['name', 'nested_dto'],
)


user_dto_response_schema = openapi.Schema(
    'UserDTO',
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'nested_dto': {
            'type': openapi.TYPE_OBJECT,
            'title': 'NestedDTO',
            'properties': {
                'a': {'type': openapi.TYPE_INTEGER},
                'b': {'type': openapi.TYPE_STRING},
            },
            'required': ['a', 'b'],
        },
        'surname': openapi.Schema(type=openapi.TYPE_STRING),
        'age': openapi.Schema(type=openapi.TYPE_INTEGER, **{'x-nullable': True}),
    },
    required=['name', 'nested_dto', 'surname', 'age'],
)


def test_get_operation():
    route = get_route(Controller.post)
    view = create_drf_view(Controller, [route])
    components = openapi.ReferenceResolver('definitions', force_init=True)
    auto_schema = SwaggerAutoSchema(view, 'path', route.http_method, components, 'request', {})

    operation = auto_schema.get_operation(['test_app', 'post'])
    parameters = [
        openapi.Parameter(
            name='data',
            in_=openapi.IN_BODY,
            required=True,
            schema=user_dto_request_schema,
        ),
        openapi.Parameter(
            name='path_param',
            in_=openapi.IN_PATH,
            description='',
            required=True,
            type=openapi.TYPE_INTEGER,
        ),
        openapi.Parameter(
            name='query_param',
            in_=openapi.IN_QUERY,
            description='',
            required=True,
            type=openapi.TYPE_INTEGER,
        ),
    ]

    assert operation == openapi.Operation(
        operation_id='Controller.post',
        responses=openapi.Responses({
            '200': openapi.Response(
                description='',
                schema=user_dto_response_schema,
            ),
        }),
        consumes=['application/json; charset=utf-8'],
        produces=['application/json; charset=utf-8'],
        description='This is post method',
        tags=['test_app'],
        parameters=parameters,
    )


def test_get_operation_with_serializer():
    route = get_route(Controller.post_with_serializer)
    view = create_drf_view(Controller, [route])
    components = openapi.ReferenceResolver('definitions', force_init=True)
    auto_schema = SwaggerAutoSchema(view, 'path', route.http_method, components, 'request', {})

    # Act
    operation = auto_schema.get_operation(['test_app', 'post'])

    # Assert
    assert operation == openapi.Operation(
        operation_id='Controller.post_with_serializer',
        responses=openapi.Responses({
            200: openapi.Response(description='', schema=user_dto_response_schema),
        }),
        consumes=['application/json'],
        produces=['application/json'],
        tags=['test_app'],
        parameters=[
            openapi.Parameter(
                name='data',
                in_=openapi.IN_BODY,
                required=True,
                schema=openapi.SchemaRef(components, 'User'),
            ),
        ],
    )

    assert components.get('User', 'definitions') == openapi.Schema(
        type='object',
        properties={
            'name': openapi.Schema('Name', type='string', minLength=1),
        },
        required=['name'],
    )


def test_get_operation_without_body():
    route = get_route(Controller.get)
    view = create_drf_view(Controller, [route])
    components = openapi.ReferenceResolver('definitions', force_init=True)
    auto_schema = SwaggerAutoSchema(view, 'path', route.http_method, components, 'request', {})

    # Act
    operation = auto_schema.get_operation(['test_app', 'post'])

    # Assert
    assert operation == openapi.Operation(
        operation_id='Controller.get',
        responses=openapi.Responses({
            '200': openapi.Response(description=''),
        }),
        consumes=['application/json'],
        produces=['application/json'],
        tags=['test_app'],
        parameters=[],
    )


def test_get_operation_without_route():
    view = create_drf_view(Controller, [])
    components = openapi.ReferenceResolver('definitions', 'parameters', force_init=True)
    auto_schema = SwaggerAutoSchema(view, 'path', 'get', components, 'request', {})
    operation = auto_schema.get_operation(['test_app', 'post'])

    assert operation == openapi.Operation(
        description='',
        operation_id='test_app_post',
        responses=openapi.Responses({
            '200': openapi.Response(description=''),
        }),
        consumes=['application/json'],
        produces=['application/json'],
        tags=['test_app'],
        parameters=[],
    )


@pytest.mark.parametrize(
    'controller_class, method_name, expected_responses', [
        (
            ControllerWithExceptions, 'declared_and_thrown', {
                '200': openapi.Response('', openapi.Schema(type=openapi.TYPE_STRING)),
                '400': openapi.Response('', openapi.Schema(
                    'CustomExceptionDTO',
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                    required=['message'],
                )),
            },
        ),
        (
            ControllerWithExceptions, 'with_custom_handler', {
                '200': openapi.Response('', openapi.Schema(type=openapi.TYPE_STRING)),
                '401': openapi.Response('', openapi.Schema(type=openapi.TYPE_INTEGER)),
            },
        ),
        (
            ControllerWithExceptions, 'not_declared_but_thrown', {
                '200': openapi.Response('', openapi.Schema(type=openapi.TYPE_STRING)),
            },
        ),
        (
            ControllerWithExceptions, 'declared_but_no_handler', {
                '200': openapi.Response('', openapi.Schema(type=openapi.TYPE_STRING)),
            },
        ),
        (
            ControllerWithProblemExceptions, 'problem_exists_dataclass_exception', {
                '200': openapi.Response('', openapi.Schema(type=openapi.TYPE_STRING)),
                '403': openapi.Response('', openapi.Schema(
                    title='ProblemExistsDataclassException',
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                        'type': openapi.Schema(type=openapi.TYPE_STRING),
                        'custom_field': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                    required=[
                        'status',
                        'title',
                        'detail',
                        'type',
                        'custom_field',
                    ],
                )),
            },
        ),
    ],
)
def test_exception_responses(controller_class, method_name: str, expected_responses):
    from winter.web.controller import get_component

    component = get_component(controller_class)
    method = component.get_method(method_name)
    route = get_route(method)

    view = create_drf_view(controller_class, [route])
    components = openapi.ReferenceResolver('definitions', 'parameters', force_init=True)
    auto_schema = SwaggerAutoSchema(view, 'path', route.http_method, components, 'request', {})

    # Act
    operation = auto_schema.get_operation(['test_app', route.http_method])

    # Assert
    assert operation.responses == openapi.Responses(expected_responses)
