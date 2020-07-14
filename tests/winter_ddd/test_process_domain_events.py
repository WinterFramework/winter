from typing import List
from typing import Union

import pytest

from winter_ddd import AggregateRoot
from winter_ddd import DomainEvent
from winter_ddd import Entity
from winter_ddd import domain_event_handler
from winter_ddd import global_domain_event_dispatcher


class CustomDomainEvent(DomainEvent):
    pass


class AnotherCustomEvent(DomainEvent):
    pass


class YetAnotherCustomEvent(DomainEvent):
    pass


@pytest.fixture
def empty_handler():
    class Handler:
        handled_domain_events = []
        handled_another_domain_events = []
        handled_many_domain_events = []
        handled_many_another_domain_events = []
        handled_union_list_domain_events = []

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
        def handle_union_list(self, domain_events: List[Union[CustomDomainEvent, AnotherCustomEvent]]):
            self.handled_union_list_domain_events.append(domain_events)

    yield Handler()


class Aggregate(Entity, AggregateRoot):
    pass


def test_process_domain_events(empty_handler):
    domain_event1 = CustomDomainEvent()
    domain_event2 = CustomDomainEvent()
    another_domain_event = AnotherCustomEvent()
    yet_another_domain_event = YetAnotherCustomEvent()

    # Act
    global_domain_event_dispatcher.dispatch([
        domain_event1,
        another_domain_event,
        yet_another_domain_event,
        domain_event2,
    ])

    # Assert
    assert empty_handler.handled_domain_events == [domain_event1, domain_event2]
    assert empty_handler.handled_another_domain_events == [another_domain_event]
    assert empty_handler.handled_many_domain_events == [[domain_event1, domain_event2]]
    assert empty_handler.handled_many_another_domain_events == [[another_domain_event]]
    assert empty_handler.handled_union_list_domain_events == [[domain_event1, another_domain_event, domain_event2]]
