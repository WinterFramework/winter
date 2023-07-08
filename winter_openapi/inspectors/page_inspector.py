import dataclasses
from typing import List

from winter.data.pagination import Page
from winter_openapi.inspection.data_formats import DataFormat
from winter_openapi.inspection.data_types import DataTypes
from winter_openapi.inspection.type_info import TypeInfo
from winter_openapi.inspectors.standard_types_inspectors import inspect_type
from winter_openapi.inspectors.standard_types_inspectors import register_type_inspector


# noinspection PyUnusedLocal
@register_type_inspector(Page)
def inspect_page(hint_class) -> TypeInfo:
    args = getattr(hint_class, '__args__', None)
    child_class = args[0] if args else str
    extra_fields = set(dataclasses.fields(hint_class.__origin__)) - set(dataclasses.fields(Page))
    child_type_info = inspect_type(child_class)
    title = child_type_info.title or child_type_info.type_.capitalize()

    return TypeInfo(
        type_=DataTypes.OBJECT,
        title=f'PageOf{title}',
        properties={
            'meta': TypeInfo(
                type_=DataTypes.OBJECT,
                title=f'PageMetaOf{title}',
                properties={
                    'total_count': TypeInfo(type_=DataTypes.INTEGER),
                    'limit': TypeInfo(type_=DataTypes.INTEGER, nullable=True),
                    'offset': TypeInfo(type_=DataTypes.INTEGER, nullable=True),
                    'previous': TypeInfo(type_=DataTypes.STRING, format_=DataFormat.URI, nullable=True),
                    'next': TypeInfo(type_=DataTypes.STRING, format_=DataFormat.URI, nullable=True),
                    **{extra_field.name: inspect_type(extra_field.type) for extra_field in extra_fields},
                },
            ),
            'objects': inspect_type(List[child_class]),
        },
    )
