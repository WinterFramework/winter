from typing import Any

from .page import Page
from .page_processor import PageProcessor
from ...output_processor import IOutputProcessorResolver


class PageOutputProcessorResolver(IOutputProcessorResolver):

    def __init__(self):
        self._page_processor = PageProcessor()

    def is_supported(self, body: Any) -> bool:
        return isinstance(body, Page)

    def get_processor(self, body: Any) -> PageProcessor:
        return self._page_processor
