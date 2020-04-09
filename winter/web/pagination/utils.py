from typing import Optional

from rest_framework.request import Request as DRFRequest
from rest_framework.utils.urls import remove_query_param
from rest_framework.utils.urls import replace_query_param

from winter.data.pagination import Page


def get_previous_page_url(page: Page, request: DRFRequest) -> Optional[str]:
    offset = page.position.offset
    limit = page.position.limit

    if not offset or limit is None:
        return None

    url = request.build_absolute_uri()
    url = replace_query_param(url, 'limit', limit)

    previous_offset = offset - limit

    if previous_offset <= 0:
        return remove_query_param(url, 'offset')

    return replace_query_param(url, 'offset', previous_offset)


def get_next_page_url(page: Page, request: DRFRequest) -> Optional[str]:
    offset = page.position.offset or 0
    limit = page.position.limit
    total = page.total_count

    if limit is None:
        return None

    next_offset = offset + limit

    if next_offset >= total:
        return None

    url = request.build_absolute_uri()
    url = replace_query_param(url, 'limit', limit)

    return replace_query_param(url, 'offset', next_offset)
