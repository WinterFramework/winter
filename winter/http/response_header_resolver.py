from rest_framework.request import Request

from winter.http.response_header import _BaseResponseHeader
from winter.type_utils import is_origin_type_subclasses
from .response_header import ResponseHeaderAnnotation
from .response_header import ResponseHeaders
from .. import ArgumentResolver
from ..core import ComponentMethodArgument


class ResponseHeaderArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        if not is_origin_type_subclasses(argument.type_, _BaseResponseHeader):
            return False
        annotations = argument.method.annotations.get(ResponseHeaderAnnotation)
        return any(annotation.argument_name == argument.name for annotation in annotations)

    def resolve_argument(self, argument: ComponentMethodArgument, request: Request, response_headers: ResponseHeaders):
        annotations = argument.method.annotations.get(ResponseHeaderAnnotation)
        annotation = next(annotation for annotation in annotations if annotation.argument_name == argument.name)
        header_name = annotation.header_name
        header = argument.type_(response_headers, header_name)
        return header
