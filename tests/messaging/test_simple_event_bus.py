from injector import ClassProvider
from injector import singleton

from winter.core import get_injector
from winter.messaging import SimpleEventBus
from winter.messaging import event_handler
from winter.messaging import get_all_event_handlers_for_package
from .events import Event1
from .events import Event2
from .events import Event3


class EventHandlers:
    def __init__(self):
        self.result = {'handlers': [], 'x': 0}

    @event_handler
    def handler1(self, event: Event1):
        self.result['handlers'].append(1)
        self.result['x'] += event.x

    @event_handler
    def handler2(self, event: Event1):
        self.result['handlers'].append(2)
        self.result['x'] += event.x

    @event_handler
    def handler3(self, event: Event3):
        self.result['handlers'].append(3)
        self.result['x'] += event.x

    def handler4(self, event: Event3):
        self.result['handlers'].append(4)
        self.result['x'] += event.x


def test_simple_event_bus():
    injector = get_injector()
    injector.binder.bind(EventHandlers, to=ClassProvider(EventHandlers), scope=singleton)

    simple_event_bus = SimpleEventBus()
    handler_methods = get_all_event_handlers_for_package('tests.messaging')
    for handler_method in handler_methods:
        simple_event_bus.register_handler(handler_method)

    result = injector.get(EventHandlers).result
    simple_event_bus.emit(Event1(10))
    assert result == {'handlers': [1, 2], 'x': 20}
    simple_event_bus.emit(Event1(20))
    assert result == {'handlers': [1, 2, 1, 2], 'x': 60}
    simple_event_bus.emit(Event2(100))
    assert result == {'handlers': [1, 2, 1, 2], 'x': 60}
    simple_event_bus.emit(Event3(1000))
    assert result == {'handlers': [1, 2, 1, 2, 3], 'x': 1060}
