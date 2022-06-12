import dataclasses
from typing import Optional

from drf_yasg import openapi
from rest_framework import serializers

import winter
import winter_django
from winter_django.view import create_drf_view
from winter_openapi import SwaggerAutoSchema
from winter.web import MediaType
from winter.web.routing import get_route


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


def test_get_operation():
    route = get_route(Controller.post)
    view = create_drf_view(Controller, [route])
    auto_schema = SwaggerAutoSchema(view, 'path', route.http_method, 'components', 'request', {})

    operation = auto_schema.get_operation(['test_app', 'post'])
    parameters = [
        openapi.Parameter(
            name='data',
            in_=openapi.IN_BODY,
            required=True,
            schema=openapi.Schema(
                title='UserDTO',
                type=openapi.TYPE_OBJECT,
                properties={
                    'name': {
                        'type': openapi.TYPE_STRING,
                    },
                    'nested_dto': {
                        'type': openapi.TYPE_OBJECT,
                        'properties': {
                            'a': {'type': openapi.TYPE_INTEGER},
                            'b': {'type': openapi.TYPE_STRING},
                        },
                        'required': ['a', 'b'],
                    },
                    'surname': {
                        'type': openapi.TYPE_STRING,
                    },
                    'age': {
                        'type': openapi.TYPE_INTEGER,
                        'x-nullable': True,
                    },
                },
                required=['name', 'nested_dto'],
            ),
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
    responses = openapi.Responses({
        '200': openapi.Response(
            description='',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'name': {
                        'type': openapi.TYPE_STRING,
                    },
                    'nested_dto': {
                        'type': openapi.TYPE_OBJECT,
                        'properties': {
                            'a': {'type': openapi.TYPE_INTEGER},
                            'b': {'type': openapi.TYPE_STRING},
                        },
                        'required': ['a', 'b'],
                    },
                    'surname': {
                        'type': openapi.TYPE_STRING,
                    },
                    'age': {
                        'type': openapi.TYPE_INTEGER,
                        'x-nullable': True,
                    },
                },
                required=['name', 'nested_dto', 'surname', 'age'],
            ),
        ),
    })

    assert operation == openapi.Operation(
        operation_id='Controller.post',
        responses=responses,
        consumes=['application/json; charset=utf-8'],
        produces=['application/json; charset=utf-8'],
        description='This is post method',
        tags=['test_app'],
        parameters=parameters,
    )


def test_get_operation_with_serializer():
    route = get_route(Controller.post_with_serializer)
    view = create_drf_view(Controller, [route])
    reference_resolver = openapi.ReferenceResolver('definitions', 'parameters', force_init=True)
    auto_schema = SwaggerAutoSchema(view, 'path', route.http_method, reference_resolver, 'request', {})

    # Act
    operation = auto_schema.get_operation(['test_app', 'post'])

    # Assert
    schema_ref = openapi.SchemaRef(
        resolver=reference_resolver,
        schema_name='User',
    )
    parameters = [
        openapi.Parameter(
            name='data',
            in_=openapi.IN_BODY,
            required=True,
            schema=schema_ref,
        ),
    ]
    responses = openapi.Responses({
        '200': openapi.Response(
            description='',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'name': {
                        'type': openapi.TYPE_STRING,
                    },
                    'nested_dto': {
                        'type': openapi.TYPE_OBJECT,
                        'properties': {
                            'a': {'type': openapi.TYPE_INTEGER},
                            'b': {'type': openapi.TYPE_STRING},
                        },
                        'required': ['a', 'b'],
                    },
                    'surname': {
                        'type': openapi.TYPE_STRING,
                    },
                    'age': {
                        'type': openapi.TYPE_INTEGER,
                        'x-nullable': True,
                    },
                },
                required=['name', 'nested_dto', 'surname', 'age'],
            ),
        ),
    })

    assert operation == openapi.Operation(
        operation_id='Controller.post_with_serializer',
        responses=responses,
        consumes=['application/json'],
        produces=['application/json'],
        tags=['test_app'],
        parameters=parameters,
    )


def test_get_operation_without_body():
    route = get_route(Controller.get)
    view = create_drf_view(Controller, [route])
    reference_resolver = openapi.ReferenceResolver('definitions', 'parameters', force_init=True)
    auto_schema = SwaggerAutoSchema(view, 'path', route.http_method, reference_resolver, 'request', {})
    operation = auto_schema.get_operation(['test_app', 'post'])
    parameters = []
    responses = openapi.Responses({
        '200': openapi.Response(description=''),
    })

    assert operation == openapi.Operation(
        operation_id='Controller.get',
        responses=responses,
        consumes=['application/json'],
        produces=['application/json'],
        tags=['test_app'],
        parameters=parameters,
    )


def test_get_operation_without_route():
    view = create_drf_view(Controller, [])
    reference_resolver = openapi.ReferenceResolver('definitions', 'parameters', force_init=True)
    auto_schema = SwaggerAutoSchema(view, 'path', 'get', reference_resolver, 'request', {})
    operation = auto_schema.get_operation(['test_app', 'post'])
    parameters = []
    responses = openapi.Responses({
        '200': openapi.Response(description=''),
    })

    assert operation == openapi.Operation(
        description='',
        operation_id='test_app_post',
        responses=responses,
        consumes=['application/json'],
        produces=['application/json'],
        tags=['test_app'],
        parameters=parameters,
    )
