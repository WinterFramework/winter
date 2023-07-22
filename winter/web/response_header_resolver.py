from typing import MutableMapping

import django.http

from winter.core import ComponentMethodArgument
from winter.core.utils.typing import is_origin_type_subclasses
from .argument_resolver import ArgumentResolver
from .response_header_annotation import ResponseHeader
from .response_header_annotation import ResponseHeaderAnnotation


class ResponseHeaderArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        if not is_origin_type_subclasses(argument.type_, ResponseHeader):
            return False
        annotations = argument.method.annotations.get(ResponseHeaderAnnotation)
        return any(annotation.argument_name == argument.name for annotation in annotations)

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: django.http.HttpRequest,
        response_headers: MutableMapping[str, str],
    ):
        annotations = argument.method.annotations.get(ResponseHeaderAnnotation)
        annotation = [annotation for annotation in annotations if annotation.argument_name == argument.name][0]
        header_name = annotation.header_name
        header = argument.type_(response_headers, header_name)
        return header
