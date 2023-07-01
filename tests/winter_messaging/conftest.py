from threading import Event as CancellationEvent
from threading import Thread

import pytest

from winter.core import get_injector
from winter_messaging_transactional.producer.publish_processor import PublishProcessor
from winter_messaging_transactional.rabbitmq import create_connection


@pytest.fixture(scope='session')
def run_processor():
    injector = get_injector()
    processor = injector.get(PublishProcessor)
    cancel_token = CancellationEvent()
    thread = Thread(target=processor.run, args=(cancel_token, 'test_flusher_id'))
    thread.start()
    yield cancel_token
    cancel_token.set()
    thread.join()


@pytest.fixture(scope='session')
def broker_channel():
    connection = create_connection()
    channel = connection.channel()
    yield channel
    channel.close()
    connection.close()
