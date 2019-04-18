import typing
import warnings

from furl import furl
from rest_framework import exceptions
from rest_framework.request import Request

from .limits import LimitsAnnotation
from .limits import MaximumLimitValueExceeded
from .page_position import PagePosition
from ..argument_resolver import ArgumentResolver
from ..core import ComponentMethodArgument
from ..exceptions import RedirectException


class PagePositionArgumentResolver(ArgumentResolver):

    def __init__(self, limit_name: str = 'limit', offset_name: str = 'offset'):
        self.limit_name = limit_name
        self.offset_name = offset_name
        self.default_limit = None
        self.maximum_limit = None
        self.redirect_to_default_limit = False

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return argument.type_ is PagePosition

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request) -> PagePosition:
        raw_limit = http_request.query_params.get(self.limit_name)
        raw_offset = http_request.query_params.get(self.offset_name)

        limit = self._parse_int_param(raw_limit, 'limit', min_value=1)
        offset = self._parse_int_param(raw_offset, 'offset', min_value=0)

        limits_annotation = argument.method.annotations.get_one_or_none(LimitsAnnotation)

        default_limit = self.default_limit
        maximum_limit = self.maximum_limit
        redirect_to_default_limit = self.redirect_to_default_limit

        if limits_annotation is not None:
            maximum_limit = limits_annotation.maximum
            default_limit = limits_annotation.default
            redirect_to_default_limit = limits_annotation.redirect_to_default

        self._try_redirect_to_default_limit(limit, default_limit, redirect_to_default_limit, http_request)

        if limit is None:
            limit = default_limit

        if limit is not None and maximum_limit is not None and limit > maximum_limit:
            raise MaximumLimitValueExceeded(maximum_limit)

        return PagePosition(limit, offset)

    def _try_redirect_to_default_limit(
            self,
            limit: typing.Optional[int],
            default_limit: typing.Optional[int],
            redirect_to_default_limit: bool,
            http_request: Request,
    ):
        if redirect_to_default_limit:
            if default_limit is None:
                warnings.warn(
                    'PagePositionArgumentResolver: redirect_to_default_limit is set to True, '
                    'however it has no effect as default_limit is not specified',
                    UserWarning,
                )
            elif limit is None:
                parsed_url = furl(http_request.get_full_path())
                parsed_url.args[self.limit_name] = default_limit
                raise RedirectException(redirect_to=parsed_url.url)

    @staticmethod
    def _parse_int_param(raw_param_value: str, param_name: str, min_value: int = 0) -> typing.Optional[int]:
        if raw_param_value is None:
            return None

        try:
            param_value = int(raw_param_value)
        except (ValueError, TypeError):
            raise exceptions.ParseError(f'Invalid "{param_name}" query parameter value: "{raw_param_value}"')

        if param_value < min_value:
            raise exceptions.ValidationError(f'Invalid "{param_name}" query parameter value: "{raw_param_value}"')
        return param_value
