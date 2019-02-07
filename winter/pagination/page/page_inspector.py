import typing

from drf_yasg import openapi

from ...schema.type_inspection import TypeInfo
from ...schema.type_inspection import inspect_type


def inspect_page(hint_class) -> TypeInfo:
    args = getattr(hint_class, '__args__', None)

    child_class = args[0] if args else str

    return TypeInfo(openapi.TYPE_OBJECT, properties={
        'meta': TypeInfo(openapi.TYPE_OBJECT, properties={
            'total_count': TypeInfo(openapi.TYPE_INTEGER),
            'limit': TypeInfo(openapi.TYPE_INTEGER, nullable=True),
            'offset': TypeInfo(openapi.TYPE_INTEGER, nullable=True),
            'previous': TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_URI, nullable=True),
            'next': TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_URI, nullable=True),
        }),
        'objects': inspect_type(typing.List[child_class]),
    })
