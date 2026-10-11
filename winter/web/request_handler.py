import json
from typing import Any
from typing import Dict

from winter.application import get_injector
from winter.components import ComponentMethod
from winter.json import JSONEncoder
from .argument_resolver import arguments_resolver
from .default_response_status import get_response_status
from .exceptions import MethodExceptionsManager
from .exceptions import ThrottleException
from .exceptions import exception_handlers_registry
from .interceptor import interceptor_registry
from .output_processor import get_output_processor
from .request import Request
from .response import Response
from .response_entity import ResponseEntity
from .response_header_serializer import response_headers_serializer
from .routing import Route
from .throttling import create_throttle_class


def handle_request(route: Route, request: Request) -> Response:
    """
    Run the whole handling pipeline for a matched route: throttling, interceptors, argument resolution,
    the API method, exception handlers, output processing and JSON encoding. Framework-agnostic: adapters
    build the Request from their own request object and send the returned Response.
    """
    method = route.method
    method_exceptions_manager = MethodExceptionsManager(method)
    response_headers: Dict[str, Any] = {}

    throttle = create_throttle_class(route)
    try:
        if throttle and not throttle.allow_request(request):
            raise ThrottleException()

        for interceptor in interceptor_registry:
            pre_handle = ComponentMethod.get_or_create(interceptor.__class__.pre_handle)
            arguments = arguments_resolver.resolve_arguments(pre_handle, request, response_headers, {'method': method})
            pre_handle(interceptor, **arguments)

        arguments = arguments_resolver.resolve_arguments(method, request, response_headers)
        api_instance = get_injector().get(method.component.component_cls)
        result = method(api_instance, **arguments)
    except Exception as exception:
        handler = method_exceptions_manager.get_handler(exception)
        method = ComponentMethod.get_or_create(handler.__class__.handle)
        try:
            arguments = arguments_resolver.resolve_arguments(
                method, request, response_headers, {'exception': exception, 'response_headers': response_headers},
            )
            result = method(handler, **arguments)
        except Exception as inner_exception:
            handler = exception_handlers_registry.get_default_handler()
            method = ComponentMethod.get_or_create(handler.__class__.handle)
            arguments = arguments_resolver.resolve_arguments(
                method, request, response_headers, {'exception': inner_exception, 'response_headers': response_headers},
            )
            result = method(handler, **arguments)

    return _to_response(request, result, method, response_headers)


def _to_response(request: Request, result: Any, method: ComponentMethod, response_headers: Dict[str, Any]) -> Response:
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

    output_processor = get_output_processor(method, body)
    if output_processor is not None:
        body = output_processor.process_output(body, request)
    if isinstance(body, Response):
        return Response(status_code=body.status_code, body=body.body, headers={**headers, **body.headers})

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
