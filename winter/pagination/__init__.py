from .limits import MaximumLimitValueExceeded
from .limits import limits
from .page import Page
from .page import inspect_page
from .page_position import PagePosition
from .page_position_argument_inspector import PagePositionArgumentsInspector
from .page_position_argument_resolver import PagePositionArgumentResolver
from .serializer import PageSerializer
from .sort import Order
from .sort import Sort
from .sort import SortDirection
from .sort import order_by
from ..exceptions.handlers import exception_handlers_registry
from ..http.exception_handlers import BadRequestExceptionHandler


def setup():
    from ..schema import register_type_inspector

    register_type_inspector(Page, func=inspect_page)
    exception_handlers_registry.add_handler(MaximumLimitValueExceeded, BadRequestExceptionHandler, auto_handle=True)
