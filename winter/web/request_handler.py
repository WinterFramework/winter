import json
from typing import Any
from typing import Collection
from typing import Iterable
from typing import Mapping

from injector import Injector

from winter.components import ComponentMethod
from winter.json import JSONEncoder
from .argument_resolver import ArgumentsResolver
from .default_response_status import get_response_status
from .exceptions import ExceptionHandlers
from .exceptions import ThrottleException
from .exceptions.handlers import exception_argument_name
from .pagination.page_position_argument_resolver import PagePositionArgumentResolver
from .path_parameters_argument_resolver import PathParametersArgumentResolver
from .query_parameters.query_parameter_argument_resolver import QueryParameterArgumentResolver
from .query_parameters.query_parameters_argument_resolver import QueryParametersArgumentResolver
from .request import Request
from .request_body_resolver import RequestBodyArgumentResolver
from .request_header_resolver import RequestHeaderArgumentResolver
from .request_scope import create_request_injector
from .response import Response
from .response_entity import ResponseEntity
from .response_header_resolver import ResponseHeaderArgumentResolver
from .response_header_serializer import response_headers_serializer
from .routing import Route
from .throttling import create_throttle_class
from .web_application import WebApplication

# The arguments mapped from the request; any other argument comes from the injector of the request
_arguments_resolver = ArgumentsResolver([
    QueryParameterArgumentResolver(),
    QueryParametersArgumentResolver(),
    PathParametersArgumentResolver(),
    RequestBodyArgumentResolver(),
    ResponseHeaderArgumentResolver(),
    PagePositionArgumentResolver(),
    RequestHeaderArgumentResolver(),
])


def check_arguments(
    app: WebApplication,
    routes: Iterable[Route],
    exception_handlers: ExceptionHandlers,
    request_types: Collection[type],
):
    """
    Fails on startup for an argument of an API method, an interceptor or an exception handler that is not mapped
    from the request and whose type the injector does not bind. Adapters bind the request types in each request.
    """
    request_types = {Request, *request_types}
    for route in routes:
        _arguments_resolver.check_arguments(route.method, app.injector, request_types)
    for interceptor in app.interceptors:
        pre_handle = ComponentMethod.get_or_create(interceptor.pre_handle)
        _arguments_resolver.check_arguments(pre_handle, app.injector, request_types, {'method'})
    for method in exception_handlers:
        _arguments_resolver.check_arguments(method, app.injector, request_types, {exception_argument_name(method)})


def handle_request(
    app: WebApplication,
    route: Route,
    request: Request,
    exception_handlers: ExceptionHandlers,
    request_values: Mapping[type, object],
) -> Response:
    """
    Run the whole handling pipeline for a matched route of the application: throttling, its interceptors, argument
    resolution, the API method, its exception handlers, output processing and JSON encoding.
    Framework-agnostic: adapters build the Request from their own request object and send the returned Response.
    The request is handled in an injector of its own, a child of the application's one, that binds the Request
    and the request values of the adapter, such as its own request object. Request-scoped values live in it.
    """
    method = route.method
    response_headers: dict[str, Any] = {}
    injector = create_request_injector(app.injector, request, request_values)

    throttle = create_throttle_class(route)
    try:
        if throttle and not throttle.allow_request(request):
            raise ThrottleException()

        for interceptor_cls in app.interceptors:
            pre_handle = ComponentMethod.get_or_create(interceptor_cls.pre_handle)
            context = {'method': method}
            arguments = _arguments_resolver.resolve_arguments(pre_handle, request, response_headers, injector, context)
            pre_handle(injector.get(interceptor_cls), **arguments)

        arguments = _arguments_resolver.resolve_arguments(method, request, response_headers, injector)
        api_instance = injector.get(method.component.component_cls)
        result = method(api_instance, **arguments)
    except Exception as exception:
        method = exception_handlers.get(type(exception))
        try:
            result = _handle_exception(method, exception, request, response_headers, injector)
        except Exception as handler_exception:
            # A failing handler is not retried: its exception goes to the handler of Exception
            method = exception_handlers.get(Exception)
            result = _handle_exception(method, handler_exception, request, response_headers, injector)

    return _to_response(request, result, method, response_headers)


def _handle_exception(
    method: ComponentMethod,
    exception: Exception,
    request: Request,
    response_headers: dict[str, Any],
    injector: Injector,
) -> Any:
    context = {exception_argument_name(method): exception}
    arguments = _arguments_resolver.resolve_arguments(method, request, response_headers, injector, context)
    handler = injector.get(method.component.component_cls)
    return method(handler, **arguments)


def _to_response(request: Request, result: Any, method: ComponentMethod, response_headers: dict[str, Any]) -> Response:
    headers = {
        name: response_headers_serializer.serialize(value, name)
        for name, value in response_headers.items()
    }
    if isinstance(result, Response):
        return Response(status_code=result.status_code, body=result.body, headers={**headers, **result.headers})

    if isinstance(result, ResponseEntity):
        body = result.entity
        status_code = result.status_code
    else:
        body = result
        status_code = get_response_status(request.method, method)

    if _is_native(body):
        return Response(status_code=status_code, body=body, headers=headers)

    headers.setdefault('content-type', 'application/json')
    content = b'' if body is None else json.dumps(body, cls=JSONEncoder).encode()
    return Response(status_code=status_code, body=content, headers=headers)


_native_response_types = ()


def register_native_response_type(type_: type):
    """
    Adapters register the response types of their framework here. An API method or an output processor
    may return such an object, and it reaches the adapter untouched.
    """
    global _native_response_types
    _native_response_types = _native_response_types + (type_,)


def _is_native(body: Any) -> bool:
    return isinstance(body, _native_response_types)
