from dataclasses import dataclass
from threading import Thread
from threading import Event as CancelationEvvent

import pytest
from injector import CallableProvider
from injector import ClassProvider
from injector import InstanceProvider
from pika.adapters.blocking_connection import BlockingChannel
from sqlalchemy import select
from sqlalchemy.engine import Engine

from winter.core import get_injector
from winter.messaging import Event
from winter.messaging import EventPublisher
from winter.messaging import topic
from winter_messaging_outbox_transacton import OutboxEventPublisher
from winter_messaging_outbox_transacton.outbox import OutboxMessage
from winter_messaging_outbox_transacton.outbox import outbox_message_table
from winter_messaging_outbox_transacton.outbox import outbox_metadata
from winter_messaging_outbox_transacton.outbox import OutboxMessageDAO
from winter_messaging_outbox_transacton.outbox import OutboxProcessor
from winter_messaging_outbox_transacton.rabbitmq import connect_to_rabbit
from winter_messaging_outbox_transacton.rabbitmq import TopologyConfig
from winter_messaging_outbox_transacton.rabbitmq import TopologyConfigurator


@pytest.fixture()
def setup_inject():
    injector = get_injector()
    engine = injector.get(Engine)

    injector.binder.bind(TopologyConfigurator, to=ClassProvider(TopologyConfigurator))
    injector.binder.bind(BlockingChannel, to=CallableProvider(connect_to_rabbit))
    injector.binder.bind(OutboxMessageDAO, to=ClassProvider(OutboxMessageDAO))
    injector.binder.bind(EventPublisher, to=ClassProvider(OutboxEventPublisher))

    configurator = injector.get(TopologyConfigurator)
    configurator.autodiscover('tests.winter_messaging_outbox_transaction')
    config = configurator.configure_topics()
    injector.binder.bind(TopologyConfig, to=InstanceProvider(config))
    outbox_metadata.drop_all(bind=engine)
    outbox_metadata.create_all(bind=engine)
    return injector


@topic('sample')
@dataclass(frozen=True)
class SampleIntegrationEvent(Event):
    entity_id: int
    name: str


def test_publish(setup_inject):
    processor = setup_inject.get(OutboxProcessor)
    cancel_token = CancelationEvvent()
    thread = Thread(target=processor.run, args=(cancel_token, ))

    event_publisher = setup_inject.get(EventPublisher)
    event = SampleIntegrationEvent(entity_id=1, name='first')
    # Act
    event_publisher.emit(event)

    thread.start()
    cancel_token.set()
    thread.join()
    # Assert
    engine = setup_inject.get(Engine)
    messages = _read_all_outbox_messages(engine)
    assert len(messages) == 1
    published_message = messages[0]
    assert published_message.id
    print(published_message.id)
    assert published_message.sent_at is not None


def _read_all_outbox_messages(engine):
    query = select(outbox_message_table)
    with engine.connect() as connection:
        records = connection.execute(query)
        return [OutboxMessage(*record) for record in records]
