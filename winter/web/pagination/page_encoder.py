import dataclasses

from winter.json import json_encoder
from winter.pagination import Page

_PAGE_FIELDS = dataclasses.fields(Page)


@json_encoder
def page_encoder(page: Page) -> dict:
    """The fields that a subclass of Page adds go to the meta."""
    return {
        'meta': {
            'total_count': page.total_count,
            'limit': page.position.limit,
            'offset': page.position.offset,
            **{
                field.name: getattr(page, field.name)
                for field in dataclasses.fields(page)
                if field not in _PAGE_FIELDS
            },
        },
        'objects': page.items,
    }
