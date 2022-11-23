from typing import List

from winter.core import Component
from winter.core import ComponentMethod
from winter.core import annotate
from winter.core.module_discovery import get_all_classes
from winter.core.module_discovery import import_recursively


class EventHandlerAnnotation:
    pass


annotation = EventHandlerAnnotation()
event_handler = annotate(annotation, single=True)


def get_all_event_handlers_for_package(package_name: str) -> List[ComponentMethod]:
    import_recursively(package_name)
    component_methods = []
    for class_name, class_ in get_all_classes(package_name):
        component = Component.get_by_cls(class_)
        for component_method in component.methods:
            if component_method.annotations.get_one_or_none(EventHandlerAnnotation):
                component_methods.append(component_method)
    return component_methods
