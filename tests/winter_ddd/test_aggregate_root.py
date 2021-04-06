from winter_ddd import AggregateRoot, DomainEvents, DomainEvent


def test_domain_events_returns_collection():
    class MyEvent(DomainEvent):
        pass

    entity = AggregateRoot()
    assert isinstance(entity.domain_events, DomainEvents)
    event = MyEvent()
    entity.domain_events.register(event)
    assert event in entity.domain_events
