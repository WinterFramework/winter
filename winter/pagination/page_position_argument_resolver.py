import typing
import warnings

from furl import furl
from rest_framework import exceptions
from rest_framework.request import Request as DRFRequest

from winter.exceptions import BadRequestException
from winter.exceptions import RedirectException
from .page_position import PagePosition
from ..argument_resolver import ArgumentResolver
from ..core import ComponentMethodArgument


class PagePositionArgumentResolver(ArgumentResolver):

    def __init__(
            self,
            limit_parameter_name: str = 'limit',
            offset_parameter_name: str = 'offset',
            default_limit: typing.Optional[int] = None,
            maximum_limit: typing.Optional[int] = None,
            redirect_to_default_limit: bool = False,
    ):
        super().__init__()
        self.limit_parameter_name = limit_parameter_name
        self.offset_parameter_name = offset_parameter_name
        self.default_limit = default_limit
        self.maximum_limit = maximum_limit
        self.redirect_to_default_limit = redirect_to_default_limit

        if default_limit is None and self.redirect_to_default_limit:
            warnings.warn(
                'PagePositionArgumentResolver: redirect_to_default_limit is set to True, '
                'however it has no effect as default_limit is not specified',
                UserWarning,
            )

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return argument.type_ is PagePosition

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: DRFRequest) -> PagePosition:
        raw_limit = http_request.query_params.get(self.limit_parameter_name)
        raw_offset = http_request.query_params.get(self.offset_parameter_name)

        limit = self._parse_int_param(raw_limit, 'limit', min_value=1)
        offset = self._parse_int_param(raw_offset, 'offset', min_value=0)

        if limit is None and self.default_limit is not None and self.redirect_to_default_limit:
            f = furl(http_request.get_full_path())
            f.args[self.limit_parameter_name] = self.default_limit
            raise RedirectException(redirect_to=f.url)

        if limit is None:
            limit = self.default_limit

        if limit is not None and self.maximum_limit is not None and limit > self.maximum_limit:
            raise BadRequestException(f'"{self.limit_parameter_name}" maximum value is exceeded: {self.maximum_limit}')

        return PagePosition(limit, offset)

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
