import dataclasses
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from winter.data.pagination import Page
from winter_openapi.inspection.type_info import TypeInfo
from winter_openapi.inspectors.standard_types_inspectors import inspect_type
from winter_openapi.inspectors.standard_types_inspectors import register_type_inspector


def create_dataclass(page_type: Type) -> Type:
    args = getattr(page_type, '__args__', None)
    child_class = args[0] if args else str
    extra_fields = set(dataclasses.fields(page_type.__origin__)) - set(dataclasses.fields(Page))
    child_type_info = inspect_type(child_class)
    title = child_type_info.title or child_type_info.type_.capitalize()

    PageMetaDataclass = dataclasses.dataclass(
        type(
            f'PageMetaOf{title}',
            (),
            {
                '__annotations__': {
                    'total_count': int,
                    'limit': Optional[int],
                    'offset': Optional[int],
                    'previous': Optional[str],
                    'next': Optional[str],
                    **{extra_field.name: extra_field.type for extra_field in extra_fields},
                },
            },
        ),
    )
    PageMetaDataclass.__doc__ = ''
    PageDataclass = dataclasses.dataclass(
        type(
            f'PageOf{title}',
            (),
            {
                '__annotations__': {
                    'meta': PageMetaDataclass,
                    'objects': List[child_class],
                },
            },
        ),
    )
    PageDataclass.__doc__ = ''
    return PageDataclass


page_to_dataclass_map: Dict[Type, Type] = {}


# noinspection PyUnusedLocal
@register_type_inspector(Page)
def inspect_page(hint_class) -> TypeInfo:
    if hint_class not in page_to_dataclass_map:
        page_to_dataclass_map[hint_class] = create_dataclass(hint_class)
    page_dataclass = page_to_dataclass_map[hint_class]
    return inspect_type(page_dataclass)
