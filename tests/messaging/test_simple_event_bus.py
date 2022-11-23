from dataclasses import dataclass

from winter.messaging import Event
from winter.messaging import SimpleEventBus
from winter.messaging import event_handler
from winter.messaging import get_all_event_handlers_for_package

result = {'handlers': [], 'x': 0}


@dataclass
class Event1(Event):
    x: int


@dataclass
class Event2(Event):
    x: int


@dataclass
class Event3(Event):
    x: int


class EventHandlers:
    @event_handler
    def handler1(self, event: Event1):
        global result
        result['handlers'].append(1)
        result['x'] += event.x

    @event_handler
    def handler2(self, event: Event1):
        global result
        result['handlers'].append(2)
        result['x'] += event.x

    @event_handler
    def handler3(self, event: Event3):
        global result
        result['handlers'].append(3)
        result['x'] += event.x

    def handler4(self, event: Event3):
        global result
        result['handlers'].append(4)
        result['x'] += event.x


def test_simple_event_bus():
    global result

    simple_event_bus = SimpleEventBus()
    handler_methods = get_all_event_handlers_for_package('tests.messaging')
    for handler_method in handler_methods:
        simple_event_bus.register_handler(handler_method)

    simple_event_bus.emit(Event1(10))
    assert result == {'handlers': [1, 2], 'x': 20}
    simple_event_bus.emit(Event1(20))
    assert result == {'handlers': [1, 2, 1, 2], 'x': 60}
    simple_event_bus.emit(Event2(100))
    assert result == {'handlers': [1, 2, 1, 2], 'x': 60}
    simple_event_bus.emit(Event3(1000))
    assert result == {'handlers': [1, 2, 1, 2, 3], 'x': 1060}
