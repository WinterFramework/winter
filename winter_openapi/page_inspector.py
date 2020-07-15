import dataclasses
from typing import List

from drf_yasg import openapi

from winter.data.pagination import Page
from .type_inspection import TypeInfo
from .type_inspection import inspect_type


def inspect_page(hint_class) -> TypeInfo:
    args = getattr(hint_class, '__args__', None)
    child_class = args[0] if args else str
    extra_fields = set(dataclasses.fields(hint_class.__origin__)) - set(dataclasses.fields(Page))

    return TypeInfo(openapi.TYPE_OBJECT, properties={
        'meta': TypeInfo(openapi.TYPE_OBJECT, properties={
            'total_count': TypeInfo(openapi.TYPE_INTEGER),
            'limit': TypeInfo(openapi.TYPE_INTEGER, nullable=True),
            'offset': TypeInfo(openapi.TYPE_INTEGER, nullable=True),
            'previous': TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_URI, nullable=True),
            'next': TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_URI, nullable=True),
            **{
                extra_field.name: inspect_type(extra_field.type)
                for extra_field in extra_fields
            },
        }),
        'objects': inspect_type(List[child_class]),
    })
