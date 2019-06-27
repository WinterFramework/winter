import typing

import dataclasses
from rest_framework.request import Request

from .request_body import RequestBodyAnnotation
from .. import ArgumentResolver
from .. import converters
from .. import type_utils
from ..core import ComponentMethodArgument


class RequestBodyArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        annotation = argument.method.annotations.get_one_or_none(RequestBodyAnnotation)
        if annotation is None:
            return False
        return annotation.argument_name == argument.name

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        fields = dataclasses.fields(argument.type_)
        input_data = self._get_input_data(fields, http_request)
        return converters.convert(input_data, argument.type_)

    def _get_input_data(
        self,
        fields: typing.List[dataclasses.Field],
        http_request: Request,
    ) -> typing.Dict[str, typing.Any]:

        input_data = {}

        for field in fields:
            field_data = self._get_field_data(field, http_request)
            if field_data is dataclasses.MISSING:
                continue
            input_data[field.name] = field_data
        return input_data

    def _get_field_data(self, field: dataclasses.Field, http_request: Request) -> typing.Any:
        if field.name not in http_request.data:
            return dataclasses.MISSING

        if type_utils.is_iterable(field.type):
            return http_request.data.getlist(field.name)
        else:
            return http_request.data.get(field.name)
