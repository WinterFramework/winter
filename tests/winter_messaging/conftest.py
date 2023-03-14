from threading import Event as CancellationEvent
from threading import Thread

import pytest
from sqlalchemy.engine import Engine

from winter.core import get_injector
from winter_messaging_outbox_transacton.inbox.inbox_message import inbox_metadata
from winter_messaging_outbox_transacton.outbox import outbox_metadata
from winter_messaging_outbox_transacton.publish_processor import PublishProcessor
from winter_messaging_outbox_transacton.rabbitmq import create_connection


@pytest.fixture(scope='session')
def messaging_infrastructure():
    injector = get_injector()
    engine = injector.get(Engine)

    outbox_metadata.drop_all(bind=engine)
    outbox_metadata.create_all(bind=engine)
    inbox_metadata.drop_all(bind=engine)
    inbox_metadata.create_all(bind=engine)


@pytest.fixture(scope='session')
def run_processor(messaging_infrastructure):
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
