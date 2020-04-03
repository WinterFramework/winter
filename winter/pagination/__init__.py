from .limits import limits
from .sort.order_by import order_by


def setup():
    from ..data.pagination.page import Page
    from ..exceptions.handlers import exception_handlers_registry
    from ..schema import register_type_inspector
    from ..web.exception_handlers import BadRequestExceptionHandler
    from .limits import MaximumLimitValueExceeded
    from .page.page_inspector import inspect_page

    register_type_inspector(Page, func=inspect_page)
    exception_handlers_registry.add_handler(MaximumLimitValueExceeded, BadRequestExceptionHandler, auto_handle=True)
