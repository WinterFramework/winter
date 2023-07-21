import json
from json import JSONDecodeError
from typing import MutableMapping

import django.http

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
        request: django.http.HttpRequest,
        response_headers: MutableMapping[str, str],
    ):
        try:
            return json_decode(json.loads(request.body), argument.type_)
        except JSONDecodeException as e:
            raise RequestDataDecodeException(e.errors)
        except JSONDecodeError as e:
            # TODO need to check content type first and return 406 if it's not application/json
            raise RequestDataDecodeException(f'Invalid JSON: {e}')
