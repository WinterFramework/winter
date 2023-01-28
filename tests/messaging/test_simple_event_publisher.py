from injector import ClassProvider
from injector import singleton

from winter.core import annotate
from winter.core import get_injector
from winter.messaging import EventHandlerRegistry
from winter.messaging import SimpleEventPublisher
from winter.messaging import event_handler
from .events import Event1
from .events import Event2
from .events import Event3


class OtherAnnotation:
    pass


other_annotation = annotate(OtherAnnotation, single=True)


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

    @other_annotation
    def handler4(self, event: Event3):  # pragma: no cover
        self.result['handlers'].append(4)
        self.result['x'] += event.x


def test_simple_event_publisher():
    injector = get_injector()
    injector.binder.bind(EventHandlers, to=ClassProvider(EventHandlers), scope=singleton)
    injector.binder.bind(EventHandlerRegistry, to=ClassProvider(EventHandlerRegistry), scope=singleton)

    simple_event_publisher = injector.get(SimpleEventPublisher)
    registry = injector.get(EventHandlerRegistry)
    registry.autodiscover('tests.messaging')

    # Act
    simple_event_publisher.emit(Event1(10))

    # Assert
    result = injector.get(EventHandlers).result
    assert result == {'handlers': [1, 2], 'x': 20}
    simple_event_publisher.emit(Event1(20))
    assert result == {'handlers': [1, 2, 1, 2], 'x': 60}
    simple_event_publisher.emit(Event2(100))
    assert result == {'handlers': [1, 2, 1, 2], 'x': 60}
    simple_event_publisher.emit(Event3(1000))
    assert result == {'handlers': [1, 2, 1, 2, 3], 'x': 1060}
