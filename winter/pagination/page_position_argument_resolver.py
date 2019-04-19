import typing

from furl import furl
from rest_framework import exceptions
from rest_framework.request import Request

from .limits import Limits
from .limits import LimitsAnnotation
from .limits import MaximumLimitValueExceeded
from .page_position import PagePosition
from ..argument_resolver import ArgumentResolver
from ..core import ComponentMethod
from ..core import ComponentMethodArgument
from ..exceptions import RedirectException


class PagePositionArgumentResolver(ArgumentResolver):

    def __init__(self, limit_name: str = 'limit', offset_name: str = 'offset'):
        self.limit_name = limit_name
        self.offset_name = offset_name
        self.limits = Limits(default=None, maximum=None, redirect_to_default=False)

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return argument.type_ is PagePosition

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request) -> PagePosition:
        page_position = self._parse_page_position(http_request)
        limits = self._get_limits(argument.method)

        if limits.redirect_to_default and page_position.limit is None and limits.default is not None:
            parsed_url = furl(http_request.get_full_path())
            parsed_url.args[self.limit_name] = limits.default
            raise RedirectException(redirect_to=parsed_url.url)

        if page_position.limit is None:
            page_position = PagePosition(limit=limits.default, offset=page_position.offset)

        if page_position.limit is not None and limits.maximum is not None and page_position.limit > limits.maximum:
            raise MaximumLimitValueExceeded(limits.maximum)

        return page_position

    def _get_limits(self, method: ComponentMethod) -> Limits:
        limits_annotation = method.annotations.get_one_or_none(LimitsAnnotation)
        if limits_annotation is not None:
            return limits_annotation.limits
        return self.limits

    def _parse_page_position(self, http_request: Request) -> PagePosition:
        raw_limit = http_request.query_params.get(self.limit_name)
        raw_offset = http_request.query_params.get(self.offset_name)
        limit = self._parse_int_param(raw_limit, self.limit_name)
        offset = self._parse_int_param(raw_offset, self.offset_name)
        return PagePosition(limit=limit, offset=offset)

    @staticmethod
    def _parse_int_param(raw_param_value: str, param_name: str) -> typing.Optional[int]:
        if not raw_param_value:
            return None

        try:
            param_value = int(raw_param_value)
        except (ValueError, TypeError):
            raise exceptions.ParseError(f'Invalid "{param_name}" query parameter value: "{raw_param_value}"')

        if param_value < 0:
            raise exceptions.ValidationError(f'Invalid "{param_name}" query parameter value: "{raw_param_value}"')
        return param_value
