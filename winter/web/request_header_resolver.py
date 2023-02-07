from typing import MutableMapping

from rest_framework.request import Request

from winter import ArgumentResolver
from winter.core import ArgumentDoesNotHaveDefault
from winter.core import ComponentMethodArgument
from winter.core.json import JSONDecodeException
from winter.core.json import json_decode
from winter.web.exceptions import RequestDataDecodeException
from winter.web.request_header_annotation import RequestHeaderAnnotation


class RequestHeaderArgumentResolver(ArgumentResolver):
    def __init__(self):
        super().__init__()
        self._cache = {}

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        annotations = argument.method.annotations.get(RequestHeaderAnnotation)
        return any(annotation.map_to == argument.name for annotation in annotations)

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: Request,
        response_headers: MutableMapping[str, str],
    ):
        request_headers = request.headers
        annotation = next(
            (
                annotation
                for annotation in argument.method.annotations.get(RequestHeaderAnnotation)
                if annotation.map_to == argument.name
            ),
        )
        header_name = annotation.name

        if header_name not in request_headers:
            try:
                return argument.get_default()
            except ArgumentDoesNotHaveDefault:
                raise RequestDataDecodeException(f'Missing required header "{header_name}"')

        try:
            return json_decode(request_headers.get(header_name), argument.type_)
        except JSONDecodeException as e:
            raise RequestDataDecodeException(e.errors)
