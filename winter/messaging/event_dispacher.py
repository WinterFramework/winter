from injector import inject

from winter.core import get_injector
from .event import Event
from .event_handler_registry import EventHandlerRegistry


class EventDispatcher:
    @inject
    def __init__(self, handler_registry: EventHandlerRegistry) -> None:
        self._handler_registry = handler_registry

    def dispatch(self, event: Event):
        injector = get_injector()
        event_type = type(event)
        handler_methods = self._handler_registry.get_handlers(event_type)
        for handler_method in handler_methods:
            handler_instance = injector.get(handler_method.component.component_cls)
            handler_method.func(handler_instance, event)