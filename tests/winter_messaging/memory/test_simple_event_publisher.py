import pytest
from injector import ClassProvider
from injector import InstanceProvider
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
    result = {'handlers': [], 'x': 0}

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


@pytest.fixture(scope='module', autouse=True)
def registry():
    injector = get_injector()
    registry = injector.get(EventHandlerRegistry)
    registry.register_class('test_consumer1', EventHandlers)
    yield
    registry.unregister_class(EventHandlers)


@pytest.mark.parametrize('event, expected_result', [
    (Event1(10), {'handlers': [1, 2], 'x': 20}),
    (Event1(20), {'handlers': [1, 2, 1, 2], 'x': 60}),
    (Event2(100), {'handlers': [1, 2, 1, 2], 'x': 60}),
    (Event3(1000), {'handlers': [1, 2, 1, 2, 3], 'x': 1060})
])
def test_simple_event_publisher(event, expected_result):
    injector = get_injector()
    simple_event_publisher = injector.get(SimpleEventPublisher)

    # Act
    simple_event_publisher.emit(event)

    # Assert
    assert EventHandlers.result == expected_result
