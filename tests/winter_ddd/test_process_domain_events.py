from typing import List
from typing import Union

import pytest

from winter.core import ComponentMethod
from winter_ddd import DomainEvent
from winter_ddd import domain_event_handler
from winter_ddd import DomainEventDispatcher


class CustomDomainEvent(DomainEvent):
    pass


class AnotherCustomEvent(DomainEvent):
    pass


class YetAnotherCustomEvent(DomainEvent):
    pass


class _TestHandler:
    handled_domain_events = []
    handled_another_domain_events = []
    handled_many_domain_events = []
    handled_many_another_domain_events = []
    handled_union_domain_events = []
    handled_union_list_domain_events = []
    handled_union_list_domain_events_new_typing_style = []

    @domain_event_handler
    def empty_handle(self, domain_event: CustomDomainEvent):
        self.handled_domain_events.append(domain_event)

    @domain_event_handler
    def handle_many(self, domain_events: List[CustomDomainEvent]):
        self.handled_many_domain_events.append(domain_events)

    @domain_event_handler
    def handle_another(self, domain_event: AnotherCustomEvent):
        self.handled_another_domain_events.append(domain_event)

    @domain_event_handler
    def handle_many_another(self, domain_events: List[AnotherCustomEvent]):
        self.handled_many_another_domain_events.append(domain_events)

    @domain_event_handler
    def handle_union(self, domain_event: Union[CustomDomainEvent, AnotherCustomEvent]):
        self.handled_union_domain_events.append(domain_event)

    @domain_event_handler
    def handle_union_list(self, domain_events: List[Union[CustomDomainEvent, AnotherCustomEvent]]):
        self.handled_union_list_domain_events.append(domain_events)

    @domain_event_handler
    def handle_union_list_new_typing_style(self, domain_events: list[CustomDomainEvent | AnotherCustomEvent]):
        self.handled_union_list_domain_events_new_typing_style.append(domain_events)


class DomainEventForOrder(DomainEvent):
    pass


class OtherDomainEventForOrder(DomainEvent):
    pass


class OrderHandler1:
    handled_domain_events = []

    @domain_event_handler
    def handle_one(self, domain_event: DomainEventForOrder):
        self.handled_domain_events.append('handle_one_1')

    @domain_event_handler
    def handle_list_one(self, domain_events: List[DomainEventForOrder]):
        self.handled_domain_events.append('handle_list_one_1')

    @domain_event_handler
    def handle_many(self, domain_events: List[Union[DomainEventForOrder, OtherDomainEventForOrder]]):
        self.handled_domain_events.append('handle_many_1')


class OrderHandler2:
    handled_domain_events = []

    @domain_event_handler
    def handle_many(self, domain_events: List[Union[DomainEventForOrder, OtherDomainEventForOrder]]):
        self.handled_domain_events.append('handle_many_2')


class OrderHandler3:
    handled_domain_events = []

    @domain_event_handler
    def handle_many(self, domain_events: Union[DomainEventForOrder, OtherDomainEventForOrder]):
        self.handled_domain_events.append('handle_many_3')

    @domain_event_handler
    def handle_one(self, domain_event: DomainEventForOrder):
        self.handled_domain_events.append('handle_one_3')


def test_process_domain_events():
    domain_event1 = CustomDomainEvent()
    domain_event2 = CustomDomainEvent()
    another_domain_event = AnotherCustomEvent()
    yet_another_domain_event = YetAnotherCustomEvent()

    dispatcher = DomainEventDispatcher()
    dispatcher.add_handlers_from_class(_TestHandler)

    # Act
    dispatcher.dispatch([
        domain_event1,
        another_domain_event,
        yet_another_domain_event,
        domain_event2,
    ])

    # Assert
    assert _TestHandler.handled_domain_events == [domain_event1, domain_event2]
    assert _TestHandler.handled_another_domain_events == [another_domain_event]
    assert _TestHandler.handled_many_domain_events == [[domain_event1, domain_event2]]
    assert _TestHandler.handled_many_another_domain_events == [[another_domain_event]]
    assert _TestHandler.handled_union_domain_events == [domain_event1, another_domain_event, domain_event2]
    assert _TestHandler.handled_union_list_domain_events == [[domain_event1, another_domain_event, domain_event2]]
    assert _TestHandler.handled_union_list_domain_events_new_typing_style == [[domain_event1, another_domain_event, domain_event2]]


def test_order_process_domain_events():
    domain_event = DomainEventForOrder()

    handled_events = []
    OrderHandler1.handled_domain_events = handled_events
    OrderHandler2.handled_domain_events = handled_events
    OrderHandler3.handled_domain_events = handled_events

    dispatcher = DomainEventDispatcher()
    dispatcher.add_handlers_from_class(OrderHandler1)
    dispatcher.add_handlers_from_class(OrderHandler2)
    dispatcher.add_handlers_from_class(OrderHandler3)

    # Act
    for _ in range(5):
        dispatcher.dispatch([
            domain_event,
        ])

    # Assert
    while handled_events:
        events = handled_events[:6]
        del handled_events[:6]
        assert events == [
            'handle_one_1',
            'handle_list_one_1',
            'handle_many_1',
            'handle_many_2',
            'handle_many_3',
            'handle_one_3',
        ]
