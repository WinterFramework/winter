from weakref import WeakKeyDictionary

from rest_framework.request import Request

from winter.http.response_header import _BaseResponseHeader
from .response_header import ResponseHeaderAnnotation
from .. import ArgumentResolver
from ..core import ComponentMethodArgument


class ResponseHeaderArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self.__response_headers_by_request = WeakKeyDictionary()

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        if not isinstance(argument.type_, type) or not issubclass(argument.type_, _BaseResponseHeader):
            return False
        annotations = argument.method.annotations.get(ResponseHeaderAnnotation)
        return any(annotation.argument_name == argument.name for annotation in annotations)

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        annotations = argument.method.annotations.get(ResponseHeaderAnnotation)
        annotation = next(annotation for annotation in annotations if annotation.argument_name == argument.name)
        header_name = annotation.header_name
        headers = self.__response_headers_by_request.get(http_request)  # TODO: do not use private access
        if headers is None:
            headers = self.__response_headers_by_request[http_request] = {}
        header = argument.type_(headers, header_name)
        return header
