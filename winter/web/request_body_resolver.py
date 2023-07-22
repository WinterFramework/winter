import json
from json import JSONDecodeError
from typing import MutableMapping

import django.http

from .argument_resolver import ArgumentResolver
from .exceptions import UnsupportedMediaTypeException
from .exceptions import RequestDataDecodeException
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
        request: django.http.HttpRequest,
        response_headers: MutableMapping[str, str],
    ):
        if 'CONTENT_TYPE' in request.META and request.META['CONTENT_TYPE'] != 'application/json':
            raise UnsupportedMediaTypeException()
        try:
            return json_decode(json.loads(request.body), argument.type_)
        except JSONDecodeException as e:
            raise RequestDataDecodeException(e.errors)
        except JSONDecodeError as e:
            raise RequestDataDecodeException(f'Invalid JSON: {e}')
