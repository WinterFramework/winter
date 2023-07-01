from http import HTTPStatus
from time import sleep

from sqlalchemy import select
from sqlalchemy.engine import Engine

from winter.core import get_injector
from winter_messaging_transactional.producer.outbox import OutboxMessage
from winter_messaging_transactional.producer.outbox import outbox_message_table

consumer_queue = 'winter.consumer_correct_events_queue'


def test_publish_without_error(api_client, run_processor, broker_channel):
    # Act
    response = api_client.post('/sample-messaging/producer/publish-event', {'id': 1, 'name': 'my-name'})

    # Assert
    assert response.status_code == HTTPStatus.OK
    sleep(2)
    messages = _read_all_outbox_messages()
    assert len(messages) == 1
    published_message = messages[0]
    assert published_message.id
    assert published_message.published_at is not None

    method, properties, body = broker_channel.basic_get(queue=consumer_queue, auto_ack=True)
    assert method is not None
    assert method.exchange == 'winter.sample-producer-topic_events_topic'
    assert method.routing_key == 'sample-producer-topic.SampleProducerNotifyEvent'
    assert properties is not None
    assert properties.message_id == str(published_message.id)
    assert properties.delivery_mode == 2
    assert properties.app_id == 'test_flusher_id'
    assert properties.content_type == 'application/json'
    assert properties.type == 'SampleProducerNotifyEvent'
    assert body == b'{"id": 1, "name": "my-name"}'


def _read_all_outbox_messages():
    injector = get_injector()
    engine = injector.get(Engine)
    query = select(outbox_message_table)
    with engine.connect() as connection:
        records = connection.execute(query)
        return [OutboxMessage(*record) for record in records]
