from winter.data.pagination import Page
from winter.web.exceptions import RequestDataDecodeException
from winter.web.exceptions import ThrottleException
from winter.web.exceptions import UnsupportedMediaTypeException
from winter.web.pagination import PagePositionArgumentResolver
from winter.web.pagination.limits import MaximumLimitValueExceeded
from .annotations import global_exception
from .annotations import register_global_exception
from .generator import generate_openapi
from .inspection.inspection import inspect_type
from .inspection.inspection import register_type_inspector
from .inspectors import PagePositionArgumentsInspector
from .inspectors import PathParametersInspector
from .inspectors import QueryParametersInspector
from .inspectors import RouteParametersInspector
from .inspectors import get_route_parameters_inspectors
from .inspectors import inspect_page
from .inspectors import register_route_parameters_inspector
from .swagger_ui import get_swagger_ui_html
from .validators import validate_missing_raises_annotations


def setup(allow_missing_raises_annotation: bool = False):
    register_global_exception(MaximumLimitValueExceeded)
    register_global_exception(ThrottleException)
    register_global_exception(RequestDataDecodeException)
    register_global_exception(UnsupportedMediaTypeException)
    register_type_inspector(Page, func=inspect_page)
    register_route_parameters_inspector(PathParametersInspector())
    register_route_parameters_inspector(QueryParametersInspector())
    register_route_parameters_inspector(PagePositionArgumentsInspector(PagePositionArgumentResolver()))
    if not allow_missing_raises_annotation:  # pragma: no cover
        validate_missing_raises_annotations()
