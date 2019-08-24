from rest_framework.request import Request

from .response_header import ResponseHeaderAnnotation
from .. import ArgumentResolver
from ..core import ComponentMethodArgument


class ResponseHeaderArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        annotations = argument.method.annotations.get(ResponseHeaderAnnotation)
        return any(annotation.argument_name == argument.name for annotation in annotations)

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        return 123
