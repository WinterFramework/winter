import os
import subprocess
import time
from datetime import datetime
from datetime import timedelta
from uuid import uuid4

from sqlalchemy import update

from winter_messaging_transactional.consumer.inbox.inbox_message import InboxMessage
from winter_messaging_transactional.consumer.inbox.inbox_message import inbox_message_table
from winter_messaging_transactional.consumer.inbox.inbox_message_dao import InboxMessageDAO
from winter_messaging_transactional.tests.helpers import read_all_inbox_messages


def test_cleanup_processed_events(database_url, rabbit_url, injector, session):
    consumer_id = 'test_consumer'
    inbox_message_1 = InboxMessage(id=uuid4(), name='event_type', consumer_id=consumer_id)
    inbox_message_2 = InboxMessage(id=uuid4(), name='event_type', consumer_id=consumer_id)

    inbox_message_dao = injector.get(InboxMessageDAO)
    inbox_message_dao.upsert(inbox_message_1)
    inbox_message_dao.upsert(inbox_message_2)
    session.commit()

    now = datetime.utcnow()
    yesterday = now - timedelta(days=2)

    statement_1 = (
        update(inbox_message_table).where(inbox_message_table.c.id == inbox_message_1.id)
        .values({inbox_message_table.c.processed_at: yesterday})
    )
    statement_2 = (
        update(inbox_message_table).where(inbox_message_table.c.id == inbox_message_2.id)
        .values({inbox_message_table.c.processed_at: now})
    )

    session.execute(statement_1)
    session.execute(statement_2)
    session.commit()

    # Act
    process = _run_inbox_cleanup_processor(database_url, rabbit_url)
    time.sleep(5)
    process.terminate()

    # Assert
    inbox_messages = read_all_inbox_messages(session)
    assert len(inbox_messages) == 1

    outbox_message = inbox_messages[0]
    assert outbox_message['id'] == inbox_message_2.id
    assert outbox_message['processed_at'] == now


def _run_inbox_cleanup_processor(database_url: str, rabbit_url: str):
    settings_path = 'winter_messaging_transactional.tests.app_sample.messaging_app'

    env = dict(
        **os.environ,
        WINTER_SETTINGS_MODULE=settings_path,
        WINTER_DATABASE_URL=database_url,
        WINTER_RABBIT_URL=rabbit_url,
        WINTER_USE_COVERAGE='true',
    )
    return subprocess.Popen(
        ['python', '-m', 'winter_messaging_transactional.run_inbox_cleanup_processor', '--interval', '3'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
