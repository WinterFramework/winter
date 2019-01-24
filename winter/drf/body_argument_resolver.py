import django.http

from .input_serializer import get_input_serializer
from ..argument_resolver import ArgumentResolver
from ..controller import ControllerMethodArgument


class DRFBodyArgumentResolver(ArgumentResolver):
    def is_supported(self, argument: ControllerMethodArgument) -> bool:
        input_serializer = get_input_serializer(argument.method.func)
        if not input_serializer:
            return False
        return input_serializer.destination_argument_name == argument.name

    def resolve_argument(self, argument: ControllerMethodArgument, http_request: django.http.HttpRequest):
        input_serializer = get_input_serializer(argument.method.func)
        serializer_class = input_serializer.class_
        serializer_args = input_serializer.args
        serializer = serializer_class(data=http_request.data, **serializer_args)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
