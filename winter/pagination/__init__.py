from .limits import MaximumLimitValueExceeded
from .limits import limits
from .page import Page
from .page import inspect_page
from .page_position import PagePosition
from .page_position_argument_inspector import PagePositionArgumentsInspector
from .page_position_argument_resolver import PagePositionArgumentResolver
from .serializer import PageSerializer
from ..exceptions.handlers import BadRequestExceptionHandler
from ..exceptions.handlers import exceptions_handler


def setup():
    from ..schema import register_type_inspector
    register_type_inspector(Page, func=inspect_page)
    exceptions_handler.add_handler(MaximumLimitValueExceeded, BadRequestExceptionHandler, auto_handle=True)
