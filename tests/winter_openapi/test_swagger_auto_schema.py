import dataclasses
from typing import Optional
from typing import Union

import pytest
from drf_yasg import openapi

import winter
from tests.api import APIWithExceptions
from tests.api import APIWithProblemExceptions
from winter.core import Component
from winter.core.json import Undefined
from winter.web import MediaType
from winter.web.routing import get_route
from winter_django.view import _create_drf_view
from winter_openapi import SwaggerAutoSchema


@dataclasses.dataclass
class NestedDTO:
    a: int
    b: str


@dataclasses.dataclass
class UserDTO:
    """
    This is a short one line description.

    This is a long multi-line description.
    It spans multiple lines.

    Attributes
    ----------
    name : str
        user name
    nested_dto: NestedDTO
        a nested dto object.
        It contains some extra data.
    surname: str, optional
        user lastname
    age: int, optional
        user age
    """
    name: str
    nested_dto: NestedDTO
    surname: str = ''
    age: Optional[int] = None


class TestAPI:

    @winter.request_body(argument_name='request_body')
    @winter.route_post(
        '{path_param}/{?query_param,another_query_param}',
        produces=[MediaType.APPLICATION_JSON_UTF8],
        consumes=[MediaType.APPLICATION_JSON_UTF8],
    )
    def post(self, path_param: int, query_param: int, request_body: UserDTO) -> UserDTO:  # pragma: no cover
        """
        This is post method

        This is a long multi-line text that provides a comprehensive description
        of all the details of the method.
        It is so long that does not fit in one line.
        So it spans multiple lines.
        :param path_param:
        :param query_param: some parameter description
        :param request_body:
        :return:
        """
        return request_body

    @winter.route_get('without-body/')
    def get(self):  # pragma: no cover
        pass


user_dto_request_schema = openapi.Schema(
    title='UserDTOInput',
    description='This is a short one line description.\n'
                '\n'
                'This is a long multi-line description.\n'
                'It spans multiple lines.',
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='user name'),
        'nested_dto': {
            'type': openapi.TYPE_OBJECT,
            'title': 'NestedDTOInput',
            'description': 'a nested dto object.\n'
                           'It contains some extra data.',

            'properties': {
                'a': {'type': openapi.TYPE_INTEGER},
                'b': {'type': openapi.TYPE_STRING},
            },
            'required': ['a', 'b'],
        },
        'surname': openapi.Schema(type=openapi.TYPE_STRING, description='user lastname'),
        'age': openapi.Schema(type=openapi.TYPE_INTEGER, description='user age', **{'x-nullable': True}),
    },
    required=['name', 'nested_dto'],
)


user_dto_response_schema = openapi.Schema(
    'UserDTO',
    description='This is a short one line description.\n'
                '\n'
                'This is a long multi-line description.\n'
                'It spans multiple lines.',
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='user name'),
        'nested_dto': {
            'type': openapi.TYPE_OBJECT,
            'title': 'NestedDTO',
            'description': 'a nested dto object.\n'
                           'It contains some extra data.',
            'properties': {
                'a': {'type': openapi.TYPE_INTEGER},
                'b': {'type': openapi.TYPE_STRING},
            },
            'required': ['a', 'b'],
        },
        'surname': openapi.Schema(type=openapi.TYPE_STRING, description='user lastname'),
        'age': openapi.Schema(type=openapi.TYPE_INTEGER, description='user age', **{'x-nullable': True}),
    },
    required=['name', 'nested_dto', 'surname', 'age'],
)


def test_get_operation():
    route = get_route(TestAPI.post)
    view = _create_drf_view(TestAPI, [route])
    components = openapi.ReferenceResolver('definitions', force_init=True)
    auto_schema = SwaggerAutoSchema(view, 'path', route.http_method, components, 'request', {})

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
            description='some parameter description',
            required=True,
            type=openapi.TYPE_INTEGER,
        ),
    ]
    expected_operation = openapi.Operation(
        operation_id='TestAPI.post',
        responses=openapi.Responses({
            '200': openapi.Response(
                description='',
                schema=user_dto_response_schema,
            ),
        }),
        consumes=['application/json; charset=utf-8'],
        produces=['application/json; charset=utf-8'],
        description='This is post method\n'
                    '\n'
                    'This is a long multi-line text that provides a comprehensive description\n'
                    'of all the details of the method.\n'
                    'It is so long that does not fit in one line.\n'
                    'So it spans multiple lines.',
        tags=['test_app'],
        parameters=parameters,
    )

    operation = auto_schema.get_operation(['test_app', 'post'])

    assert operation == expected_operation


def test_get_operation_without_body():
    route = get_route(TestAPI.get)
    view = _create_drf_view(TestAPI, [route])
    components = openapi.ReferenceResolver('definitions', force_init=True)
    auto_schema = SwaggerAutoSchema(view, 'path', route.http_method, components, 'request', {})

    # Act
    operation = auto_schema.get_operation(['test_app', 'post'])

    # Assert
    assert operation == openapi.Operation(
        operation_id='TestAPI.get',
        responses=openapi.Responses({
            '200': openapi.Response(description=''),
        }),
        consumes=['application/json'],
        produces=['application/json'],
        tags=['test_app'],
        parameters=[],
    )


def test_get_operation_without_route():
    view = _create_drf_view(TestAPI, [])
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
    'api_class, method_name, expected_responses', [
        (
            APIWithExceptions, 'declared_and_thrown', {
                '200': openapi.Response('', openapi.Schema(type=openapi.TYPE_STRING)),
                '400': openapi.Response('', openapi.Schema(
                    'CustomExceptionDTO',
                    description='CustomExceptionDTO(message: str)',
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                    required=['message'],
                )),
            },
        ),
        (
            APIWithExceptions, 'with_custom_handler', {
                '200': openapi.Response('', openapi.Schema(type=openapi.TYPE_STRING)),
                '401': openapi.Response('', openapi.Schema(type=openapi.TYPE_INTEGER)),
            },
        ),
        (
            APIWithExceptions, 'not_declared_but_thrown', {
                '200': openapi.Response('', openapi.Schema(type=openapi.TYPE_STRING)),
            },
        ),
        (
            APIWithExceptions, 'declared_but_no_handler', {
                '200': openapi.Response('', openapi.Schema(type=openapi.TYPE_STRING)),
            },
        ),
        (
            APIWithProblemExceptions, 'problem_exists_dataclass_exception', {
                '200': openapi.Response('', openapi.Schema(type=openapi.TYPE_STRING)),
                '403': openapi.Response('', openapi.Schema(
                    title='ProblemExistsDataclassException',
                    description='ProblemExistsDataclassException(status: int, title: str, detail: str, type: str, '
                                'custom_field: str)',
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
def test_exception_responses(api_class, method_name: str, expected_responses):
    component = Component.get_by_cls(api_class)
    method = component.get_method(method_name)
    route = get_route(method)

    view = _create_drf_view(api_class, [route])
    components = openapi.ReferenceResolver('definitions', 'parameters', force_init=True)
    auto_schema = SwaggerAutoSchema(view, 'path', route.http_method, components, 'request', {})

    # Act
    operation = auto_schema.get_operation(['test_app', route.http_method])

    # Assert
    assert operation.responses == openapi.Responses(expected_responses)


def test_undefined_fields():
    @dataclasses.dataclass
    class RequestBody:
        """Some description"""
        field_a: Union[str, Undefined]
        field_b: Union[str, Undefined] = Undefined()

    class SomeAPI:
        @winter.route_post()
        @winter.request_body('body')
        def post(self, body: RequestBody):  # pragma: no cover
            pass

    route = get_route(SomeAPI.post)
    view = _create_drf_view(TestAPI, [route])
    components = openapi.ReferenceResolver('definitions', force_init=True)
    auto_schema = SwaggerAutoSchema(view, 'path', route.http_method, components, 'request', {})

    parameters = [
        openapi.Parameter(
            name='data',
            in_=openapi.IN_BODY,
            required=True,
            schema=openapi.Schema(
                title='RequestBodyInput',
                description='Some description',
                type=openapi.TYPE_OBJECT,
                properties={
                    'field_a': openapi.Schema(type=openapi.TYPE_STRING),
                    'field_b': openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        ),
    ]
    expected_operation = openapi.Operation(
        operation_id='SomeAPI.post',
        responses=openapi.Responses({
            '200': openapi.Response(
                description='',
            ),
        }),
        consumes=['application/json'],
        produces=['application/json'],
        tags=['test_app'],
        parameters=parameters,
    )

    operation = auto_schema.get_operation(['test_app', 'post'])

    assert operation == expected_operation
