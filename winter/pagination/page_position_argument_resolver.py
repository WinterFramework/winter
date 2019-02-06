import typing

from rest_framework import exceptions
from rest_framework.request import Request as DRFRequest

from .page_position import PagePosition
from ..argument_resolver import ArgumentResolver
from ..controller import ControllerMethodArgument


class PagePositionArgumentResolver(ArgumentResolver):

    def __init__(self, limit_parameter_name: str = 'limit', offset_parameter_name: str = 'offset'):
        self.limit_parameter_name = limit_parameter_name
        self.offset_parameter_name = offset_parameter_name

    def is_supported(self, argument: ControllerMethodArgument) -> bool:
        return argument.type_ == PagePosition

    def resolve_argument(self, argument: ControllerMethodArgument, http_request: DRFRequest) -> PagePosition:
        raw_limit = http_request.query_params.get(self.limit_parameter_name)
        raw_offset = http_request.query_params.get(self.offset_parameter_name)

        limit = self._parse_param(raw_limit, 'limit')
        offset = self._parse_param(raw_offset, 'offset')
        return PagePosition(limit, offset)

    def _parse_param(self, raw_param_value: str, param_name: str) -> typing.Optional[int]:
        if raw_param_value is None:
            return raw_param_value
        try:
            param_value = int(raw_param_value)
        except (ValueError, TypeError):
            raise exceptions.ParseError(f'Invalid "{param_name}" query parameter value: "{raw_param_value}"')

        if param_value <= 0:
            raise exceptions.ValidationError(f'Invalid "{param_name}" query parameter value: "{raw_param_value}"')
        return param_value
