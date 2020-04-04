import typing

from .page_processor import PageProcessor
from ...data.pagination import Page
from winter.web.output_processor import IOutputProcessorResolver


class PageOutputProcessorResolver(IOutputProcessorResolver):

    def __init__(self):
        self._page_processor = PageProcessor()

    def is_supported(self, body: typing.Any) -> bool:
        return isinstance(body, Page)

    def get_processor(self, body: typing.Any) -> PageProcessor:
        return self._page_processor
