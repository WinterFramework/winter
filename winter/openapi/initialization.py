from winter.pagination import Page
from winter.web.exceptions import RequestDataDecodeException
from winter.web.exceptions import ThrottleException
from winter.web.exceptions import UnsupportedMediaTypeException
from winter.web.pagination.page_position_argument_resolver import PagePositionArgumentResolver
from winter.web.pagination.limits import MaximumLimitValueExceeded
from .annotations import register_global_exception
from .inspection.inspection import register_type_inspector
from .inspectors import PagePositionArgumentsInspector
from .inspectors import PathParametersInspector
from .inspectors import QueryParametersInspector
from .inspectors import inspect_page
from .inspectors import register_route_parameters_inspector

_initialized = False


def initialize():
    """
    Registers the standard inspectors and global exceptions once per process, before the first spec is generated.
    Process-global until these registries belong to an application: docs/architecture.md, Current deviations.
    """
    global _initialized
    if _initialized:
        return
    register_global_exception(MaximumLimitValueExceeded)
    register_global_exception(ThrottleException)
    register_global_exception(RequestDataDecodeException)
    register_global_exception(UnsupportedMediaTypeException)
    register_type_inspector(Page, func=inspect_page)
    register_route_parameters_inspector(PathParametersInspector())
    register_route_parameters_inspector(QueryParametersInspector())
    register_route_parameters_inspector(PagePositionArgumentsInspector(PagePositionArgumentResolver()))
    _initialized = True
