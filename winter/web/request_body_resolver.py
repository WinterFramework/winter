from typing import MutableMapping

from rest_framework.request import Request

from .argument_resolver import ArgumentResolver
from .exceptions.exceptions import RequestDataDecodeException
from .request_body_annotation import RequestBodyAnnotation
from ..core import ComponentMethodArgument
from ..core.json import JSONDecodeException
from ..core.json import json_decode


class RequestBodyArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        annotation = argument.method.annotations.get_one_or_none(RequestBodyAnnotation)
        if annotation is None:
            return False
        return annotation.argument_name == argument.name

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: Request,
        response_headers: MutableMapping[str, str],
    ):
        try:
            return json_decode(request.data, argument.type_)
        except JSONDecodeException as e:
            raise RequestDataDecodeException(e.errors)
