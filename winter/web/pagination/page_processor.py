from typing import Dict

from rest_framework.request import Request as DRFRequest

from winter.data.pagination import Page
from winter.web.output_processor import IOutputProcessor
from .utils import get_next_page_url
from .utils import get_previous_page_url


class PageProcessor(IOutputProcessor):

    def process_output(self, output: Page, request: DRFRequest) -> Dict:
        return {
            'meta': {
                'total_count': output.total_count,
                'limit': output.position.limit,
                'offset': output.position.offset,
                'previous': get_previous_page_url(output, request),
                'next': get_next_page_url(output, request),
            },
            'objects': output.items,
        }
