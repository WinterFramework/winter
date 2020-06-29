import typing

import pytest

from winter_ddd import AggregateRoot
from winter_ddd import DomainEvent
from winter_ddd import Entity
from winter_ddd import domain_event_handler
from winter_ddd import process_domain_events
from winter_ddd.domain_event_handler import delete_domain_event_handler
from winter_ddd.domain_event_handler import get_instance_getter
from winter_ddd.domain_event_handler import set_instance_getter


class CustomDomainEvent(DomainEvent):
    pass


class AnotherCustomEvent(DomainEvent):
    pass


@pytest.fixture
def empty_handler():
    class Handler:
        handled_domain_events = []
        handled_another_domain_events = []
        handled_many_domain_events = []
        handled_many_another_domain_events = []

        @domain_event_handler
        def empty_handle(self, domain_event: CustomDomainEvent):
            self.handled_domain_events.append(domain_event)

        @domain_event_handler
        def handle_many(self, domain_events: typing.List[CustomDomainEvent]):
            self.handled_many_domain_events.append(domain_events)

        @domain_event_handler
        def handle_another(self, domain_event: AnotherCustomEvent):
            self.handled_another_domain_events.append(domain_event)

        @domain_event_handler
        def handle_many_another(self, domain_events: typing.List[AnotherCustomEvent]):
            self.handled_many_another_domain_events.append(domain_events)

    yield Handler()
    delete_domain_event_handler(CustomDomainEvent)


class Aggregate(Entity, AggregateRoot):
    pass


@pytest.fixture
def instance_getter():
    def instance_getter(cls):
        return cls()

    old_instance_getter = get_instance_getter()
    set_instance_getter(instance_getter)
    yield
    set_instance_getter(old_instance_getter)


@pytest.mark.usefixtures('instance_getter')
def test_process_domain_events(empty_handler):
    domain_event1 = CustomDomainEvent()
    domain_event2 = CustomDomainEvent()
    another_domain_event = AnotherCustomEvent()

    # Act
    process_domain_events([domain_event1, another_domain_event, domain_event2])

    # Assert
    assert empty_handler.handled_domain_events == [domain_event1, domain_event2]
    assert empty_handler.handled_another_domain_events == [another_domain_event]
    assert empty_handler.handled_many_domain_events == [[domain_event1, domain_event2],]
    assert empty_handler.handled_many_another_domain_events == [[another_domain_event]]
