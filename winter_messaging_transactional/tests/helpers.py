import os
import subprocess
from time import sleep
from typing import Any
from typing import Callable

from sqlalchemy import select

from winter_messaging_transactional.consumer.inbox.inbox_message import inbox_message_table
from winter_messaging_transactional.producer.outbox import outbox_message_table


class WaitingForResultException(Exception):
    pass


def wait_for_result(func: Callable, seconds: int) -> Any:  # pragma: no cover
    for _ in range(seconds):
        result = func()
        if result:
            return result
        sleep(1)

    raise WaitingForResultException(f'No result found after {seconds} seconds')


def run_processor(database_url: str, rabbit_url: str):
    settings_path = 'winter_messaging_transactional.tests.app_sample.messaging_app'

    env = dict(
        **os.environ,
        WINTER_SETTINGS_MODULE=settings_path,
        WINTER_DATABASE_URL=database_url,
        WINTER_RABBIT_URL=rabbit_url,
        USE_COVERAGE='true',
    )
    return subprocess.Popen(
        ['python', '-m', 'winter_messaging_transactional.run_processor'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )


def run_consumer(database_url: str, rabbit_url: str, consumer_id: str):
    settings_path = 'winter_messaging_transactional.tests.app_sample.messaging_app'

    env = dict(
        **os.environ,
        WINTER_SETTINGS_MODULE=settings_path,
        WINTER_DATABASE_URL=database_url,
        WINTER_RABBIT_URL=rabbit_url,
        USE_COVERAGE='true',
    )
    return subprocess.Popen(
        ['python', '-m', 'winter_messaging_transactional.run_consumer', consumer_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )


def read_all_inbox_messages(session):
    query = select([
        inbox_message_table.c.id,
        inbox_message_table.c.consumer_id,
        inbox_message_table.c.name,
        inbox_message_table.c.counter,
        inbox_message_table.c.received_at,
        inbox_message_table.c.processed_at,
    ])
    rows = session.execute(query)
    return [dict(**row) for row in rows]


def read_all_outbox_messages(session):
    query = select([
        outbox_message_table.c.id,
        outbox_message_table.c.message_id,
        outbox_message_table.c.topic,
        outbox_message_table.c.type,
        outbox_message_table.c.body,
        outbox_message_table.c.created_at,
        outbox_message_table.c.published_at,
    ])
    rows = session.execute(query)
    return [dict(**row) for row in rows]

