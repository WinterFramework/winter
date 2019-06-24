import typing

import dataclasses
import pydantic
from rest_framework.request import Request

from .input_data import InputDataAnnotation
from .input_data_exception_handler import InvalidInputDataException
from .. import ArgumentResolver
from ..core import ComponentMethodArgument


class InputDataArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self._origin_dataclasses = {}
        self._pydantic_dataclasses = {}

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return self._get_origin_dataclass(argument) is not None

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        origin_dataclass  = self._get_origin_dataclass(argument)
        request_data = {
            key: http_request.data.get(key)
            for key in http_request.data.keys()
            if key in origin_dataclass.__annotations__
        }
        validated_data = self._get_validated_data(request_data, argument)
        return origin_dataclass(**validated_data)

    def _get_origin_dataclass(
        self,
        argument: ComponentMethodArgument,
    ) -> typing.Optional[typing.Tuple[typing.Type, typing.Type]]:

        if argument in self._origin_dataclasses:
            return self._origin_dataclasses[argument]

        input_data_annotation = argument.method.annotations.get_one_or_none(InputDataAnnotation)
        if input_data_annotation is None or argument.name != input_data_annotation.to:
            self._origin_dataclasses[argument] = None
            return None

        origin_dataclass = input_data_annotation.input_data_class

        self._origin_dataclasses[argument] = origin_dataclass

        pydantic_dataclass = pydantic.dataclasses.dataclass(
            type('PydanticInputDataclass', (), {'__annotations__': origin_dataclass.__annotations__.copy()}),
        )

        self._pydantic_dataclasses[argument] = pydantic_dataclass

        return origin_dataclass

    def _get_validated_data(self, request_data: typing.Dict[str, typing.Any], argument: ComponentMethodArgument):
        pydantic_dataclass = self._pydantic_dataclasses[argument]
        try:
            return dataclasses.asdict(pydantic_dataclass(**request_data))
        except pydantic.error_wrappers.ValidationError as exception:
            errors = exception.errors()
            data = {
                error['loc'][0]: error['msg']
                for error in errors
            }
            raise InvalidInputDataException(data)
