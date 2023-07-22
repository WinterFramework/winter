from typing import MutableMapping
from typing import Optional

import django.http

from winter import ArgumentResolver
from winter.core import ArgumentDoesNotHaveDefault
from winter.core import ComponentMethodArgument
from winter.core.json import JSONDecodeException
from winter.core.json import json_decode
from winter.web.exceptions import RequestDataDecodeException
from winter.web.request_header_annotation import RequestHeaderAnnotation


class RequestHeaderArgumentResolver(ArgumentResolver):
    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return self._get_annotation(argument) is not None

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: django.http.HttpRequest,
        response_headers: MutableMapping[str, str],
    ):
        request_headers = request.headers
        annotation = self._get_annotation(argument)
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

    def _get_annotation(self, argument: ComponentMethodArgument) -> Optional[RequestHeaderAnnotation]:
        return next(
            (
                annotation
                for annotation in argument.method.annotations.get(RequestHeaderAnnotation)
                if annotation.map_to == argument.name
            ),
            None,
        )
