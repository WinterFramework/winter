from typing import Dict

import dataclasses
from rest_framework.request import Request as DRFRequest

from winter.data.pagination import Page
from winter.web.output_processor import IOutputProcessor
from .utils import get_next_page_url
from .utils import get_previous_page_url


class PageProcessor(IOutputProcessor):

    def process_output(self, output: Page, request: DRFRequest) -> Dict:
        extra_fields = set(dataclasses.fields(output)) - set(dataclasses.fields(Page))
        return {
            'meta': {
                'total_count': output.total_count,
                'limit': output.position.limit,
                'offset': output.position.offset,
                'previous': get_previous_page_url(output, request),
                'next': get_next_page_url(output, request),
                **{
                    extra_field.name: getattr(output, extra_field.name)
                    for extra_field in extra_fields
                },
            },
            'objects': output.items,
        }
