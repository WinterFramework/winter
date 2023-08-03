import json
import time
from uuid import uuid4

import pytest
from testcontainers.rabbitmq import RabbitMqContainer

from winter.core.json import JSONEncoder

from winter_messaging_transactional.tests.conftest import event_consumer
from winter_messaging_transactional.tests.helpers import get_rabbitmq_url
from winter_messaging_transactional.tests.helpers import read_all_inbox_messages
from winter_messaging_transactional.tests.app_sample.dao import ConsumerDAO
from winter_messaging_transactional.tests.app_sample.events import SampleEvent
from winter_messaging_transactional.tests.app_sample.events import RetryableEvent
from winter_messaging_transactional.consumer.inbox.inbox_message import InboxMessage
from winter_messaging_transactional.consumer.inbox.inbox_message_dao import InboxMessageDAO
from winter_messaging_transactional.producer.outbox import OutboxEventPublisher
from winter_messaging_transactional.producer.outbox import OutboxMessage
from winter_messaging_transactional.producer.outbox import OutboxMessageDAO
from winter_messaging_transactional.tests.helpers import run_consumer
from winter_messaging_transactional.tests.helpers import run_processor
from winter_messaging_transactional.tests.helpers import wait_for_result


def test_consume_without_error(database_url, rabbit_url, event_processor, injector, session):
    event_publisher = injector.get(OutboxEventPublisher)
    payload_id = 1
    payload = 'consume_without_error'

    consumer_dao = injector.get(ConsumerDAO)

    # Act
    with event_consumer(database_url, rabbit_url, consumber_id='consumer_correct'):
        event = SampleEvent(id=payload_id, payload=payload)
        event_publisher.emit(event)
        session.commit()
        consumed_event = wait_for_result(seconds=10, func=lambda: consumer_dao.find_by_id(payload_id))

    # Assert
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
        event = RetryableEvent(id=payload_id, payload=payload, can_be_handled_on_retry=can_be_handled_on_retry)
        event_publisher.emit(event)
        session.commit()
        time.sleep(40)

    # Assert
    inbox_messages = read_all_inbox_messages(session)
    assert len(inbox_messages) == 1

    event_message = inbox_messages[0]
    assert event_message['consumer_id'] == 'consumer_timeout'
    assert event_message['name'] == 'RetryableEvent'
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


def test_consume_interrupt_during_timeout(database_url, rabbit_url, event_processor, injector, session):
    event_publisher = injector.get(OutboxEventPublisher)
    payload_id = 1
    payload = 'consumer_timeout'

    # Act
    process = run_consumer(database_url=database_url, rabbit_url=rabbit_url, consumer_id='consumer_timeout')
    event = RetryableEvent(id=payload_id, payload=payload)
    event_publisher.emit(event)
    session.commit()
    default_timeout = 15
    time.sleep(default_timeout // 2)

    # Worker should not attempt to handle the event again after the TimeoutException if it has received the INT signal.
    process.terminate()
    time.sleep(default_timeout)

    # Assert
    output = process.stdout.read1().decode('utf-8')
    timeout_error_message = "WARNING:event_handling:Timeout is raised during execution _dispatch_event with args: ()," \
                            " kwargs: {'event': RetryableEvent(id=1, payload='consumer_timeout'"

    # Because there should not be a second attempt to handle the event, we expect only one timeout message in the logs
    assert output.count(timeout_error_message) == 1

    inbox_messages = read_all_inbox_messages(session)
    assert len(inbox_messages) == 1

    event_message = inbox_messages[0]
    assert event_message['consumer_id'] == 'consumer_timeout'
    assert event_message['name'] == 'RetryableEvent'
    assert event_message['counter'] == 0
    assert event_message['received_at']
    assert event_message['processed_at'] is None

    consumer_dao = injector.get(ConsumerDAO)
    consumed_event = consumer_dao.find_by_id(payload_id)
    assert consumed_event is None


@pytest.mark.parametrize('can_be_handled_on_retry', (True, False))
def test_consume_with_error(database_url, rabbit_url, event_processor, injector, session, can_be_handled_on_retry):
    event_publisher = injector.get(OutboxEventPublisher)
    payload_id = 1
    payload = 'consume_with_error'

    # Act
    with event_consumer(database_url, rabbit_url, consumber_id='consumer_with_error'):
        event = RetryableEvent(id=payload_id, payload=payload, can_be_handled_on_retry=can_be_handled_on_retry)
        event_publisher.emit(event)
        session.commit()
        time.sleep(10)

    # Assert
    inbox_messages = read_all_inbox_messages(session)
    assert len(inbox_messages) == 1

    event_message = inbox_messages[0]
    assert event_message['consumer_id'] == 'consumer_with_error'
    assert event_message['name'] == 'RetryableEvent'
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


def test_consumer_with_recreate_connection(database_url, injector, session):
    event_publisher = injector.get(OutboxEventPublisher)
    event_1 = SampleEvent(id=1, payload='payload')
    event_2 = SampleEvent(id=2, payload='payload')
    consumer_dao = injector.get(ConsumerDAO)

    with RabbitMqContainer("rabbitmq:3.11.5") as rabbitmq_container:
        params = rabbitmq_container.get_connection_params()
        rabbit_url = get_rabbitmq_url(params)

        processor = run_processor(database_url, rabbit_url)
        time.sleep(2)
        consumer = run_consumer(database_url, rabbit_url, consumer_id='consumer_correct')
        time.sleep(2)

        event_publisher.emit(event_1)
        session.commit()
        wait_for_result(seconds=10, func=lambda: consumer_dao.find_by_id(event_1.id))

        # Act
        rabbitmq_container.exec('rabbitmqctl close_all_user_connections guest test_reason')
        event_publisher.emit(event_2)
        session.commit()

        wait_for_result(func=lambda: consumer_dao.find_by_id(event_2.id), seconds=10)
        processor.terminate()
        consumer.terminate()
