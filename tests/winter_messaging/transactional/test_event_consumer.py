from sqlalchemy import select
from sqlalchemy.engine import Engine

from winter.core import get_injector
from winter_messaging_transactional.consumer import ConsumerWorker
from winter_messaging_transactional.consumer.inbox.inbox_message import InboxMessage
from winter_messaging_transactional.consumer.inbox.inbox_message import inbox_message_table


def test_consume_without_error(broker_channel):
    broker_channel.basic_publish()
    worker = ConsumerWorker()
    # Act
    worker.start('test_consumer_id')

    # Assert
    messages = _read_all_inbox_messages()
    assert len(messages) == 1
    consumed_message = messages[0]
    assert consumed_message.id
    assert consumed_message.received_at is not None
    assert consumed_message.processed_at is not None


def _read_all_inbox_messages():
    injector = get_injector()
    engine = injector.get(Engine)
    query = select(inbox_message_table)
    with engine.connect() as connection:
        records = connection.execute(query)
        return [InboxMessage(*record) for record in records]