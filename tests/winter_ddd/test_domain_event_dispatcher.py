from winter_ddd import DomainEventDispatcher
from tests.winter_ddd.test_domain_event_dispatcher_fixture.events import DomainEvent1
from tests.winter_ddd.test_domain_event_dispatcher_fixture.events import DomainEvent2


def test_add_handlers_from_package():
    dispatcher = DomainEventDispatcher()
    dispatcher.add_handlers_from_package('tests.winter_ddd.test_domain_event_dispatcher_fixture')
    event1 = DomainEvent1()
    event2 = DomainEvent2()

    # Act
    dispatcher.dispatch([event1, event2])

    # Assert
    # Intentionally importing here to make sure that handlers are registered without explicit imports
    from tests.winter_ddd.test_domain_event_dispatcher_fixture.handler1 import Handler1
    from tests.winter_ddd.test_domain_event_dispatcher_fixture.subpackage.handler2 import Handler2
    assert len(Handler1.received_events) == 1
    assert len(Handler2.received_events) == 1
    assert Handler1.received_events[0] is event1
    assert Handler2.received_events[0] is event2
