from typing import Optional

import django.http
from furl import furl

from winter.data.pagination import Page


def get_previous_page_url(page: Page, request: django.http.HttpRequest) -> Optional[str]:
    offset = page.position.offset
    limit = page.position.limit

    if not offset or limit is None:
        return None

    url = furl(request.build_absolute_uri())
    url.query.set([('limit', limit)])

    previous_offset = offset - limit

    if previous_offset <= 0:
        url.query.remove('offset')
    else:
        url.query.set([('offset', previous_offset)])

    return url.tostr()


def get_next_page_url(page: Page, request: django.http.HttpRequest) -> Optional[str]:
    offset = page.position.offset or 0
    limit = page.position.limit
    total = page.total_count

    if limit is None:
        return None

    next_offset = offset + limit

    if next_offset >= total:
        return None

    url = furl(request.build_absolute_uri())
    url.query.set([
        ('limit', limit),
        ('offset', next_offset),
    ])
    return url.tostr()
