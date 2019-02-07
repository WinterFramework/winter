from .page import Page
from .page_position import PagePosition
from .serializer import PageSerializer
from .page_position_argument_resolver import PagePositionArgumentResolver
from .page_position_argument_inspector import PagePositionArgumentInspector


def setup():
    from . import page
    page.setup()
