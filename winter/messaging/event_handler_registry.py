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
from .topic_annotation import TopicAnnotation


class EventHandlerRegistry:
    def __init__(self):
        self._event_type_to_handler_map: MutableMapping[Type[Event], List[ComponentMethod]] = defaultdict(list)
        self._event_name_to_event_type_map = defaultdict()

    def _register_handler(self, handler_method: ComponentMethod):
        event_type: Type[Event] = handler_method.arguments[0].type_
        self._event_type_to_handler_map[event_type].append(handler_method)
        self._register_event(event_type)

    def _register_event(self, event_type: Type[Event]):
        self._event_name_to_event_type_map[event_type.__name__] = event_type

    def get_handlers(self, event_type: Type[Event]) -> Iterable[ComponentMethod]:
        return self._event_type_to_handler_map[event_type]

    def get_all_handlers(self) -> Iterable[ComponentMethod]:
        for handlers in self._event_type_to_handler_map.values():
            for handler in handlers:
                yield handler

    def get_event_type(self, event_type_name: str) -> Type[Event]:
        return self._event_name_to_event_type_map[event_type_name]

    def get_all_event_types(self) -> Iterable[Type[Event]]:
        return self._event_name_to_event_type_map.values()

    def autodiscover(self, package_name: str):
        import_recursively(package_name)
        for class_name, class_ in get_all_classes(package_name):
            component = Component.get_by_cls(class_)
            for component_method in component.methods:
                event_handler_annotation = component_method.annotations.get_one_or_none(EventHandlerAnnotation)
                if event_handler_annotation:
                    self._register_handler(component_method)
            topic_annotation = component.annotations.get_one_or_none(TopicAnnotation)
            if topic_annotation:
                self._register_event(class_)
