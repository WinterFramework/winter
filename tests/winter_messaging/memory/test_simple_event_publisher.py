from injector import ClassProvider
from injector import singleton

from winter.core import get_injector
from winter.messaging import EventHandlerRegistry
from winter.messaging import SimpleEventPublisher
from .events import Event1
from .events import Event2
from .events import Event3
from .handlers import EventHandlers


def test_simple_event_publisher():
    injector = get_injector()
    injector.binder.bind(EventHandlers, to=ClassProvider(EventHandlers), scope=singleton)
    injector.binder.bind(EventHandlerRegistry, to=ClassProvider(EventHandlerRegistry), scope=singleton)

    simple_event_publisher = injector.get(SimpleEventPublisher)
    registry = injector.get(EventHandlerRegistry)
    registry.autodiscover('test_consumer1', 'tests.winter_messaging.memory')

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
