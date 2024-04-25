from contextlib import contextmanager
from typing import List
from typing import Union

from injector import ClassProvider
from injector import singleton

from winter.core import annotate
from winter.core import get_injector
from winter.messaging import EventSubscriptionRegistry
from winter.messaging import SimpleEventPublisher
from winter.messaging import event_handler
from .events import Event1
from .events import Event2
from .events import Event3
from .events import Event4


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

    @event_handler
    def handler5(self, event: Event4):
        self.result['handlers'].append(5)
        self.result['x'] += event.x

    @event_handler
    def handler6(self, events: List[Event4]):
        for event in events:
            self.result['handlers'].append(6)
            self.result['x'] += event.x

    @event_handler
    def handler7(self, event: Union[Event1, Event3]):
        self.result['handlers'].append(7)
        self.result['x'] += event.x

    @event_handler
    def handler8(self, events: List[Union[Event1, Event3]]):
        for event in events:
            self.result['handlers'].append(8)
            self.result['x'] += event.x


class GroupingHandler:
    handled_events = []

    @event_handler
    def handle_union(self, domain_events: Union[Event1, Event3]):
        self.handled_events.append('handle_union')

    @event_handler
    def handle_list_of_union(self, domain_events: List[Union[Event1, Event3]]):
        self.handled_events.append('handle_list_of_union')


@contextmanager
def manager_for_test(name: str):
    try:
        yield
    finally:
        return name


def test_simple_event_publisher():
    injector = get_injector()
    injector.binder.bind(EventHandlers, to=ClassProvider(EventHandlers), scope=singleton)
    injector.binder.bind(EventSubscriptionRegistry, to=ClassProvider(EventSubscriptionRegistry), scope=singleton)

    simple_event_publisher = injector.get(SimpleEventPublisher)
    registry = injector.get(EventSubscriptionRegistry)
    registry.autodiscover('tests.messaging')
    event_handlers = injector.get(EventHandlers)
    event_handlers.result = {'handlers': [], 'x': 0}

    # Act
    simple_event_publisher.emit(Event1(10))

    # Assert
    # emit event
    result = event_handlers.result
    assert result == {'handlers': [1, 2, 7, 8], 'x': 40}

    # emit same event again
    simple_event_publisher.emit(Event1(20))
    assert result == {'handlers': [1, 2, 7, 8, 1, 2, 7, 8], 'x': 120}

    # emit event with no handlers
    simple_event_publisher.emit(Event2(100))
    assert result == {'handlers': [1, 2, 7, 8, 1, 2, 7, 8], 'x': 120}

    # emit event with other annotation
    simple_event_publisher.emit(Event3(200))
    assert result == {'handlers': [1, 2, 7, 8, 1, 2, 7, 8, 3, 7, 8], 'x': 720}

    # emit event with handler for single event and list of events
    simple_event_publisher.emit(Event4(1000))
    assert result == {'handlers': [1, 2, 7, 8, 1, 2, 7, 8, 3, 7, 8, 5, 6], 'x': 2720}

    # Test emit_many
    event_handlers.result = {'handlers': [], 'x': 0}

    # emit event
    simple_event_publisher.emit_many([Event1(10)])
    result = event_handlers.result
    assert result == {'handlers': [1, 2, 7, 8], 'x': 40}

    # emit same event twice
    simple_event_publisher.emit_many([Event3(200), Event3(200)])
    assert result == {'handlers': [1, 2, 7, 8, 3, 3, 7, 7, 8, 8], 'x': 1240}

    # emit different events
    simple_event_publisher.emit_many([Event1(10), Event2(100), Event3(200), Event4(1000)])
    assert result == {'handlers': [1, 2, 7, 8, 3, 3, 7, 7, 8, 8, 1, 2, 7, 7, 8, 8, 3, 5, 6],  'x': 3880}

    # Test emit when events grouped by subscription with modified handler_method
    handled_events = []
    GroupingHandler.handled_domain_events = handled_events

    for event_type, subscriptions in registry._event_type_to_subscription_map.items():
        if event_type in [type(Event1), type(Event3)]:
            decorated_subscriptions = []

            for subscription in subscriptions:
                manager = manager_for_test(subscription.handler_method.__name__)
                subscription.handler_method.func = manager(subscription.handler_method.func)

            registry._event_type_to_subscription_map[event_type] = decorated_subscriptions

    simple_event_publisher.emit_many([Event1(10), Event3(200)])

    # Assert
    while handled_events:
        events = handled_events[:5]
        del handled_events[:5]
        assert events == [
            'handle_union',
            'handle_union',
            'handle_list_of_union',
        ]
