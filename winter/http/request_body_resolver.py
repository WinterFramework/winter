import typing

import dataclasses
import pydantic
from rest_framework.request import Request

from .request_body import RequestBodyAnnotation
from .request_body_exception_handler import InvalidRequestBodyException
from .. import ArgumentResolver
from .. import type_utils
from ..core import ComponentMethodArgument
from ..type_utils import is_iterable


class InputDataArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self._pydantic_dataclasses = {}

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return argument.method.annotations.get_one_or_none(RequestBodyAnnotation) is not None

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        fields = dataclasses.fields(argument.type_)

        input_data, missing_fields = self._get_input_data(fields, http_request)
        errors = {}

        pydantic_dataclass = self._get_pydantic_dataclass(argument.type_)

        validated_data = {}

        try:
            validated_data = dataclasses.asdict(pydantic_dataclass(**input_data))
        except pydantic.error_wrappers.ValidationError as exception:
            self._update_errors(errors, exception.errors(), missing_fields)
        if errors:
            raise InvalidRequestBodyException(errors, missing_fields)
        return argument.type_(**validated_data)

    def _get_input_data(self, fields: typing.List[dataclasses.Field], http_request: Request):

        input_data = {}
        missing_fields = set()

        for field in fields:
            field_data = self._get_field_data(field, http_request)
            is_missing = field_data is dataclasses.MISSING
            if is_missing:
                missing_fields.add(field.name)
            input_data[field.name] = field_data
        return input_data, missing_fields

    def _get_field_data(self, field: dataclasses.Field, http_request: Request) -> typing.Any:
        if is_iterable(field.type):
            field_data = http_request.data.getlist(field.name)
        else:
            field_data = http_request.data.get(field.name)

        if not field_data:
            field_data = self._get_default(field)
        else:
            field_data = dataclasses.MISSING
        return field_data

    def _get_default(self, field: dataclasses.Field) -> typing.Any:
        if field.default is not dataclasses.MISSING:
            return field.default
        elif type_utils.is_optional(field.type):
            return None
        else:
            return dataclasses.MISSING

    def _get_pydantic_dataclass(self, origin_dataclass: typing.Type) -> typing.Type:
        if origin_dataclass in self._pydantic_dataclasses:
            return self._pydantic_dataclasses[origin_dataclass]

        pydantic_dataclass = pydantic.dataclasses.dataclass(
            type('PydanticInputDataclass', (), {'__annotations__': origin_dataclass.__annotations__.copy()}),
        )

        self._pydantic_dataclasses[origin_dataclass] = pydantic_dataclass

        return pydantic_dataclass

    def _update_errors(self, errors: typing.Dict[str, str], pydantic_errors: typing.Dict, missing_fields: typing.Set):
        for error in pydantic_errors:
            field = error['loc'][0]
            if field not in missing_fields:
                errors[field] = error['msg']
