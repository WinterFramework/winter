import json
import time
from uuid import uuid4

import pytest
from winter.core.json import JSONEncoder

from winter_messaging_transactional.tests.conftest import event_consumer
from winter_messaging_transactional.tests.helpers import read_all_inbox_messages
from winter_messaging_transactional.tests.app_sample.dao import ConsumerDAO
from winter_messaging_transactional.tests.app_sample.events import SampleEvent
from winter_messaging_transactional.consumer.inbox.inbox_message import InboxMessage
from winter_messaging_transactional.consumer.inbox.inbox_message_dao import InboxMessageDAO
from winter_messaging_transactional.producer.outbox import OutboxEventPublisher
from winter_messaging_transactional.producer.outbox import OutboxMessage
from winter_messaging_transactional.producer.outbox import OutboxMessageDAO


def test_consume_without_error(database_url, rabbit_url, event_processor, injector, session):
    event_publisher = injector.get(OutboxEventPublisher)
    payload_id = 1
    payload = 'consume_without_error'

    # Act
    with event_consumer(database_url, rabbit_url, consumber_id='consumer_correct'):
        event = SampleEvent(id=payload_id, payload=payload)
        event_publisher.emit(event)
        session.commit()
        time.sleep(15)

    # Assert
    consumer_dao = injector.get(ConsumerDAO)
    consumed_event = consumer_dao.find_by_id(payload_id)
    assert consumed_event
    assert consumed_event['id'] == payload_id
    assert consumed_event['payload'] == payload

    inbox_messages = read_all_inbox_messages(session)
    assert len(inbox_messages) == 1
    event_message = inbox_messages[0]
    assert event_message['consumer_id'] == 'consumer_correct'
    assert event_message['name'] == 'SampleEvent'
    assert event_message['counter'] == 0
    assert event_message['received_at']
    assert event_message['processed_at']



@pytest.mark.parametrize('can_be_handled_on_retry', (True, False))
def test_consume_with_timeout(database_url, rabbit_url, event_processor, injector, session, can_be_handled_on_retry):
    event_publisher = injector.get(OutboxEventPublisher)
    payload_id = 1
    payload = 'consumer_timeout'

    # Act
    with event_consumer(database_url, rabbit_url, consumber_id='consumer_timeout'):
        event = SampleEvent(id=payload_id, payload=payload, can_be_handled_on_retry=can_be_handled_on_retry)
        event_publisher.emit(event)
        session.commit()
        time.sleep(60)

    # Assert
    inbox_messages = read_all_inbox_messages(session)
    assert len(inbox_messages) == 1

    event_message = inbox_messages[0]
    assert event_message['consumer_id'] == 'consumer_timeout'
    assert event_message['name'] == 'SampleEvent'
    assert event_message['counter'] == 0
    assert event_message['received_at']
    if can_be_handled_on_retry:
        assert event_message['processed_at']
    else:
        assert event_message['processed_at'] is None

    consumer_dao = injector.get(ConsumerDAO)
    consumed_event = consumer_dao.find_by_id(payload_id)

    if can_be_handled_on_retry:
        assert consumed_event
        assert consumed_event['id'] == payload_id
        assert consumed_event['payload'] == payload
    else:
        assert consumed_event is None


@pytest.mark.parametrize('can_be_handled_on_retry', (True, False))
def test_consume_with_error(database_url, rabbit_url, event_processor, injector, session, can_be_handled_on_retry):
    event_publisher = injector.get(OutboxEventPublisher)
    payload_id = 1
    payload = 'consume_with_error'

    # Act
    with event_consumer(database_url, rabbit_url, consumber_id='consumer_with_error'):
        event = SampleEvent(id=payload_id, payload=payload, can_be_handled_on_retry=can_be_handled_on_retry)
        event_publisher.emit(event)
        session.commit()
        time.sleep(10)

    # Assert
    inbox_messages = read_all_inbox_messages(session)
    assert len(inbox_messages) == 1

    event_message = inbox_messages[0]
    assert event_message['consumer_id'] == 'consumer_with_error'
    assert event_message['name'] == 'SampleEvent'
    assert event_message['counter'] == (1 if can_be_handled_on_retry else 3)
    assert event_message['received_at']
    if can_be_handled_on_retry:
        assert event_message['processed_at']
    else:
        assert event_message['processed_at'] is None

    consumer_dao = injector.get(ConsumerDAO)
    consumed_event_1 = consumer_dao.find_by_id(payload_id)
    consumed_event_2 = consumer_dao.find_by_id(payload_id + 1)

    if can_be_handled_on_retry:
        assert consumed_event_1
        assert consumed_event_2
        assert consumed_event_1['payload'] == payload
        assert consumed_event_2['payload'] == payload
    else:
        assert consumed_event_1 is None
        assert consumed_event_2 is None


def test_consumer_already_processed_event(database_url, rabbit_url, event_processor, injector, session):
    payload_id = 1
    consumber_id = 'consumer_correct'
    message_id = uuid4()

    outbox_message_dao = injector.get(OutboxMessageDAO)

    outbox_message = OutboxMessage(
        message_id=message_id,
        topic='sample-topic',
        type='SampleEvent',
        body=json.dumps(dict(payload='payload'), ensure_ascii=False, cls=JSONEncoder),
    )
    outbox_message_dao.save(outbox_message)

    inbox_message_dao = injector.get(InboxMessageDAO)
    inbox_message = InboxMessage(
        id=message_id,
        consumer_id=consumber_id,
        name='SampleEvent'
    )
    inbox_message_dao.upsert(inbox_message)
    inbox_message_dao.mark_as_processed(message_id, consumber_id)
    session.commit()

    # Act
    with event_consumer(database_url, rabbit_url, consumber_id=consumber_id):
        time.sleep(5)

    consumer_dao = injector.get(ConsumerDAO)
    consumed_event = consumer_dao.find_by_id(payload_id)
    assert consumed_event is None

    inbox_messages = read_all_inbox_messages(session)
    assert len(inbox_messages) == 1
    inbox_message = inbox_messages[0]
    assert inbox_message['id'] == message_id
    assert inbox_message['counter'] == 1
    assert inbox_message['processed_at']

