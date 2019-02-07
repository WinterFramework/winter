from .page import Page
from .page import inspect_page
from .page_position import PagePosition
from .page_position_argument_inspector import PagePositionArgumentInspector
from .page_position_argument_resolver import PagePositionArgumentResolver
from .serializer import PageSerializer


def setup():
    from ..schema import register_type_inspector
    register_type_inspector(Page, func=inspect_page)
