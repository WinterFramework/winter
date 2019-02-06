from .page import Page
from .page_inspector import inspect_page
from .page_processor import PageProcessor
from .page_processor_resolver import PageOutputProcessorResolver


def setup():
    from ...schema import register_type_inspector
    register_type_inspector(Page, func=inspect_page)
