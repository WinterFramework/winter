from collections import defaultdict
from typing import Iterable
from typing import List
from typing import MutableMapping
from typing import Type

from winter.core import Component
from winter.core import ComponentMethod
from winter.core.module_discovery import get_all_classes
from winter.core.module_discovery import import_recursively
from .event import Event
from .event_handler import EventHandlerAnnotation


class EventHandlerRegistry:
    def __init__(self):
        self._event_type_to_handler_methods: MutableMapping[Type[Event], List[ComponentMethod]] = defaultdict(list)
        self._event_name_to_event_type_map = defaultdict()

    def register_handler(self, handler_method: ComponentMethod):
        event_type: Type[Event] = self.get_event_type_of_handler(handler_method)
        self._event_type_to_handler_methods[event_type].append(handler_method)
        self.register_event(event_type)

    def register_event(self, event_type: Type[Event]):
        self._event_name_to_event_type_map[event_type.__name__] = event_type

    def get_event_type_of_handler(self, handler_method: ComponentMethod) -> Type[Event]:
        return handler_method.arguments[0].type_

    def get_handlers(self, event_type: Type[Event]) -> Iterable[ComponentMethod]:
        return self._event_type_to_handler_methods[event_type]

    def autodiscover(self, package_name: str):
        import_recursively(package_name)
        for class_name, class_ in get_all_classes(package_name):
            component = Component.get_by_cls(class_)
            for component_method in component.methods:
                if component_method.annotations.get_one_or_none(EventHandlerAnnotation):
                    self.register_handler(component_method)
