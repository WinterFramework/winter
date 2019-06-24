import typing

import dataclasses
import pydantic
from rest_framework.request import Request

from .input_data import InputDataAnnotation
from .input_data_exception_handler import InvalidInputDataException
from .. import ArgumentResolver
from .. import type_utils
from ..core import ComponentMethodArgument
from ..type_utils import is_iterable


class InputDataArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self._origin_dataclasses = {}
        self._pydantic_dataclasses = {}

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return self._get_origin_dataclass(argument) is not None

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        origin_dataclass = self._get_origin_dataclass(argument)
        validated_data = self._get_validated_data(http_request, argument)
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

    def _get_validated_data(self, http_request: Request, argument: ComponentMethodArgument):
        origin_dataclass = self._get_origin_dataclass(argument)
        fields = dataclasses.fields(origin_dataclass)

        input_data, missing_fields = self._get_input_data(fields, http_request)
        errors = {}

        if missing_fields:
            errors['non_field_error'] = f'Missing fields: {",".join(missing_fields)}'

        pydantic_dataclass = self._pydantic_dataclasses[argument]

        validated_data = {}

        try:
            validated_data = dataclasses.asdict(pydantic_dataclass(**input_data))
        except pydantic.error_wrappers.ValidationError as exception:
            self._update_errors(errors, exception.errors(), missing_fields)
        if errors:
            raise InvalidInputDataException(errors)
        return validated_data

    def _get_input_data(self, fields: typing.List[dataclasses.Field], http_request: Request):

        input_data = {}
        missing_fields = set()

        for field in fields:
            field_data = self._get_field_data(field, missing_fields, http_request)
            input_data[field.name] = field_data
        return input_data, missing_fields

    def _get_field_data(self, field: dataclasses.Field, missing_fields: typing.Set, http_request: Request):
        if is_iterable(field.type):
            field_data = http_request.data.getlist(field.name)
        else:
            field_data = http_request.data.get(field.name)

        if not field_data:
            field_data = self._get_default(field, missing_fields)
        return field_data

    def _get_default(self, field: dataclasses.Field, missing_fields: typing.Set):
        if field.default is not dataclasses.MISSING:
            return field.default
        elif type_utils.is_optional(field.type):
            return None
        else:
            missing_fields.add(field.name)
            return dataclasses.MISSING

    def _update_errors(self, errors: typing.Dict[str, str], pydantic_errors: typing.Dict, missing_fields: typing.Set):
        for error in pydantic_errors:
            field = error['loc'][0]
            if field not in missing_fields:
                errors[field] = error['msg']
