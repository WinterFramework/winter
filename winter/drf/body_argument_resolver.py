from rest_framework.request import Request

from .input_serializer import get_input_serializer
from ..argument_resolver import ArgumentResolver
from ..core import ComponentMethodArgument


class DRFBodyArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        input_serializer = get_input_serializer(argument.method)
        if input_serializer is None:
            return False
        return input_serializer.destination_argument_name == argument.name

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        input_serializer = get_input_serializer(argument.method)
        serializer_class = input_serializer.class_
        serializer_kwargs = input_serializer.kwargs
        serializer = serializer_class(data=http_request.data, **serializer_kwargs)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
