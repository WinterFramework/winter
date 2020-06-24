from typing import Any

from winter.data.pagination import Page
from winter.web.output_processor import IOutputProcessorResolver
from .page_processor import PageProcessor


class PageOutputProcessorResolver(IOutputProcessorResolver):

    def __init__(self):
        self._page_processor = PageProcessor()

    def is_supported(self, body: Any) -> bool:
        return isinstance(body, Page)

    def get_processor(self, body: Any) -> PageProcessor:
        return self._page_processor
