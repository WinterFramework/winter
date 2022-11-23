from collections import defaultdict
from typing import List
from typing import MutableMapping
from typing import Type

from winter.core import ComponentMethod
from winter.core import get_injector
from .event import Event
from .event_bus import EventBus


class SimpleEventBus(EventBus):
    def __init__(self):
        self._handler_methods: MutableMapping[Type, List[ComponentMethod]] = defaultdict(list)

    def emit(self, event: Event):
        injector = get_injector()
        event_type = type(event)
        for handler_method in self._handler_methods[event_type]:
            handler_instance = injector.get(handler_method.component.component_cls)
            handler_method.func(handler_instance, event)

    def register_handler(self, handler_method: ComponentMethod):
        self._handler_methods[handler_method.arguments[0].type_].append(handler_method)
