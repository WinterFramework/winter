from winter_ddd import DomainEvent
from winter_ddd import DomainEvents


def test_new_domain_events_is_empty():
    domain_events = DomainEvents()
    assert len(domain_events) == 0
    assert list(domain_events) == []


def test_domain_events_registers_events():
    domain_events = DomainEvents()
    event1 = DomainEvent()
    event2 = DomainEvent()
    domain_events.register(event1)
    domain_events.register(event2)
    assert len(domain_events) == 2
    assert list(domain_events) == [event1, event2]


def test_domain_events_doesnt_clears_events():
    domain_events = DomainEvents()
    domain_events.register(DomainEvent())
    domain_events.register(DomainEvent())
    list(domain_events)
    assert len(domain_events) == 2


def test_domain_events_clear():
    domain_events = DomainEvents()
    domain_events.register(DomainEvent())
    domain_events.register(DomainEvent())
    domain_events.clear()
    assert len(domain_events) == 0
