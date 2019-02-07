from .page import inspect_page
from .page import Page
from .page_position import PagePosition
from .serializer import PageSerializer
from .page_position_argument_resolver import PagePositionArgumentResolver
from .page_position_argument_inspector import PagePositionArgumentInspector


def setup():
    from ..schema import register_type_inspector
    register_type_inspector(Page, func=inspect_page)
