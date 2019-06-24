import typing

import pydantic
from rest_framework.request import Request

from .input_data import InputDataAnnotation
from .input_data_exception_handler import InvalidInputDataException
from .. import ArgumentResolver
from ..core import ComponentMethodArgument


class InputDataArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self._cache = {}

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return self._get_input_dataclass(argument) is not None

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        input_dataclass = self._get_input_dataclass(argument)
        request_data = {
            key: http_request.data.get(key)
            for key in http_request.data.keys()
        }
        try:
            return input_dataclass(**request_data)
        except pydantic.error_wrappers.ValidationError as exception:
            errors = exception.errors()
            data = {
                error['loc'][0]: error['msg']
                for error in errors
            }
            raise InvalidInputDataException(data)

    def _get_input_dataclass(self, argument: ComponentMethodArgument) -> typing.Optional[str]:
        input_data_annotation = argument.method.annotations.get_one_or_none(InputDataAnnotation)
        if input_data_annotation is None or argument.name != input_data_annotation.to:
            self._cache[argument] = None
            return None
        self._cache[argument] = input_data_annotation
        return input_data_annotation.input_data_class
