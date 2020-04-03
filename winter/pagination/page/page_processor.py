import typing

from rest_framework.request import Request as DRFRequest

from ..utils import get_next_page_url
from ..utils import get_previous_page_url
from ...data.pagination import Page
from ...output_processor import IOutputProcessor


class PageProcessor(IOutputProcessor):

    def process_output(self, output: Page, request: DRFRequest) -> typing.Dict:
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
