import dataclasses
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from winter.pagination import Page
from winter.openapi.inspection.type_info import TypeInfo
from winter.openapi.inspectors.standard_types_inspectors import inspect_type
from winter.openapi.inspectors.standard_types_inspectors import type_inspector


def create_dataclass(page_type: Type) -> Type:
    args = getattr(page_type, '__args__', None)
    child_class = args[0] if args else str
    page_class = page_type.__origin__
    page_field_names = {field.name for field in dataclasses.fields(Page)}
    # In the order the class declares them, so that the spec is the same from run to run
    extra_fields = [field for field in dataclasses.fields(page_class) if field.name not in page_field_names]
    child_type_info = inspect_type(child_class)
    title = child_type_info.title or child_type_info.type_.capitalize()

    PageMetaDataclass = dataclasses.dataclass(
        type(
            f'{page_class.__name__}MetaOf{title}',
            (),
            {
                '__annotations__': {
                    'total_count': int,
                    'limit': Optional[int],
                    'offset': Optional[int],
                    **{extra_field.name: extra_field.type for extra_field in extra_fields},
                },
            },
        ),
    )
    PageMetaDataclass.__doc__ = ''
    PageDataclass = dataclasses.dataclass(
        type(
            f'{page_class.__name__}Of{title}',
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
@type_inspector(Page)
def inspect_page(hint_class) -> TypeInfo:
    if hint_class not in page_to_dataclass_map:
        page_to_dataclass_map[hint_class] = create_dataclass(hint_class)
    page_dataclass = page_to_dataclass_map[hint_class]
    return inspect_type(page_dataclass)
