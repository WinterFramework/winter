import os
import subprocess
import time
from datetime import datetime
from datetime import timedelta

from sqlalchemy import update

from winter_messaging_transactional.producer.outbox import OutboxEventPublisher
from winter_messaging_transactional.producer.outbox import outbox_message_table
from winter_messaging_transactional.tests.app_sample.events import SampleEvent
from winter_messaging_transactional.tests.helpers import read_all_outbox_messages


def test_cleanup_published_events(database_url, rabbit_url, injector, session):
    event_publisher = injector.get(OutboxEventPublisher)
    event_1 = SampleEvent(id=1, payload='payload 1')
    event_2 = SampleEvent(id=2, payload='payload 2')
    event_publisher.emit(event_1)
    event_publisher.emit(event_2)
    session.commit()

    now = datetime.utcnow()
    yesterday = now - timedelta(days=2)

    statement_1 = (
        update(outbox_message_table).where(outbox_message_table.c.id == 1)
        .values({outbox_message_table.c.published_at: yesterday})
    )
    statement_2 = (
        update(outbox_message_table).where(outbox_message_table.c.id == 2)
        .values({outbox_message_table.c.published_at: now})
    )

    session.execute(statement_1)
    session.execute(statement_2)
    session.commit()

    # Act
    process = _run_cleanup_processor(database_url, rabbit_url)
    time.sleep(20)
    process.terminate()

    # Assert
    outbox_messages = read_all_outbox_messages(session)
    assert len(outbox_messages) == 1

    outbox_message = outbox_messages[0]
    assert outbox_message['id'] == 2
    assert outbox_message['published_at'] == now


def _run_cleanup_processor(database_url: str, rabbit_url: str):
    settings_path = 'winter_messaging_transactional.tests.app_sample.messaging_app'

    env = dict(
        **os.environ,
        WINTER_SETTINGS_MODULE=settings_path,
        WINTER_DATABASE_URL=database_url,
        WINTER_RABBIT_URL=rabbit_url,
        USE_COVERAGE='false',
    )
    return subprocess.Popen(
        ['python', '-m', 'winter_messaging_transactional.run_outbox_cleanup_processor'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
