from rest_framework.request import Request

from .request_body import RequestBodyAnnotation
from .. import ArgumentResolver
from .. import converters
from ..core import ComponentMethodArgument


class RequestBodyArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        annotation = argument.method.annotations.get_one_or_none(RequestBodyAnnotation)
        if annotation is None:
            return False
        return annotation.argument_name == argument.name

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        return converters.convert(http_request.data, argument.type_)
