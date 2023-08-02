import time

from urllib.parse import urlparse

from pika import BlockingConnection
from pika import ConnectionParameters
from pika import PlainCredentials

from winter_messaging_transactional.naming_convention import get_consumer_queue
from winter_messaging_transactional.naming_convention import get_exchange_name
from winter_messaging_transactional.naming_convention import get_routing_key
from winter_messaging_transactional.producer.outbox import OutboxEventPublisher
from winter_messaging_transactional.tests.app_sample.events import SampleEvent
from winter_messaging_transactional.tests.helpers import read_all_outbox_messages
from winter_messaging_transactional.tests.helpers import run_processor


def test_publish_events(database_url, rabbit_url, injector, session):
    event_publisher = injector.get(OutboxEventPublisher)
    event = SampleEvent(id=1, payload='payload')
    event_publisher.emit(event)
    session.commit()

    # Act
    process = run_processor(database_url, rabbit_url)
    time.sleep(5)
    process.terminate()

    # Assert
    outbox_messages = read_all_outbox_messages(session)
    assert len(outbox_messages) == 1

    outbox_message = outbox_messages[0]
    assert outbox_message['message_id'] is not None
    assert outbox_message['body'] == '{"id": 1, "payload": "payload"}'
    assert outbox_message['topic'] == 'sample-topic'
    assert outbox_message['type'] == 'SampleEvent'
    assert outbox_message['created_at'] is not None
    assert outbox_message['published_at'] is not None


def test_publish_event_to_not_existed_exchange(database_url, injector, session, rabbit_url):
    event_publisher = injector.get(OutboxEventPublisher)
    event = SampleEvent(id=1, payload='payload')
    event_publisher.emit(event)

    # Act
    process = run_processor(database_url, rabbit_url)
    time.sleep(5)

    connection = _create_rabbitmq_connection(rabbit_url)
    channel = connection.channel()
    channel.exchange_delete(get_exchange_name('sample-topic'))
    session.commit()
    time.sleep(5)
    output = process.stdout.read1().decode('utf-8')
    process.terminate()

    assert output.find('Publishing processor error. Message not published:') != -1
    assert output.find("ChannelClosedByBroker: (404, \"NOT_FOUND - no exchange 'winter.sample-topic_events_topic' in vhost") != -1


def test_publish_event_to_not_existed_queue(database_url, injector, session, rabbit_url):
    event_publisher = injector.get(OutboxEventPublisher)
    event = SampleEvent(id=1, payload='payload')
    event_publisher.emit(event)

    # Act
    process = run_processor(database_url, rabbit_url)
    time.sleep(5)

    connection = _create_rabbitmq_connection(rabbit_url)
    channel = connection.channel()

    for consumer_id in ['consumer_correct', 'consumer_timeout', 'consumer_with_error']:
        channel.queue_delete(get_consumer_queue(consumer_id))

    session.commit()
    time.sleep(5)
    output = process.stdout.read1().decode('utf-8')
    process.terminate()

    assert output.find('The message was not routed to any queue.') != -1


def test_publish_event_to_get_nack_from_broker(database_url, injector, session, rabbit_url):
    event_publisher = injector.get(OutboxEventPublisher)
    event = SampleEvent(id=1, payload='payload')
    event_publisher.emit(event)
    event_publisher.emit(event)

    # Act
    process = run_processor(database_url, rabbit_url)
    time.sleep(10)

    connection = _create_rabbitmq_connection(rabbit_url)
    channel = connection.channel()
    channel.queue_declare(queue='limitted_queue', arguments={'x-overflow': 'reject-publish', 'x-max-length': 1})
    channel.queue_bind(
        queue='limitted_queue',
        exchange=get_exchange_name('sample-topic'),
        routing_key=get_routing_key('sample-topic', 'SampleEvent')
    )
    session.commit()
    time.sleep(10)

    output = process.stdout.read1().decode('utf-8')
    process.terminate()

    assert output.find("pika.exceptions.NackError: 0 message(s) NACKed") != -1
    assert output.find('Publishing processor error. Message not published:') != -1
    assert output.find("rabbitmq_client.MessageNackedException: Published failed.") != -1
    assert output.find("routing key: sample-topic.SampleEvent; exchange: winter.sample-topic_events_topic. "
                       "Check configuration settings for confirmation") != -1
    assert output.find("Publishing processor aborted due to an error") != -1


def _create_rabbitmq_connection(rabbit_url: str):
    parsed_url = urlparse(rabbit_url)
    params = ConnectionParameters(
        host=parsed_url.hostname,
        port=parsed_url.port,
        credentials=PlainCredentials(parsed_url.username, parsed_url.password),
        heartbeat=600,
        blocked_connection_timeout=300,
    )
    return BlockingConnection(params)
