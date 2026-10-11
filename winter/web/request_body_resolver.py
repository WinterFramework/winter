import json
from json import JSONDecodeError
from typing import MutableMapping


from .argument_resolver import ArgumentResolver
from .exceptions import UnsupportedMediaTypeException
from .exceptions import RequestDataDecodeException
from .request_body_annotation import RequestBodyAnnotation
from winter.web.request import Request
from winter.components import ComponentMethodArgument
from winter.json import JSONDecodeException
from winter.json import json_decode


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
        content_type = request.headers.get('Content-Type')
        if content_type is not None and content_type != 'application/json':
            raise UnsupportedMediaTypeException()
        try:
            return json_decode(json.loads(request.body), argument.type_)
        except JSONDecodeException as e:
            raise RequestDataDecodeException(e.errors)
        except JSONDecodeError as e:
            raise RequestDataDecodeException(f'Invalid JSON: {e}')
