import dataclasses
from datetime import datetime
from datetime import timedelta
from typing import Iterable

from injector import inject
from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.engine import Engine

from .outbox_message import OutboxMessage
from .outbox_message import outbox_message_table


class OutboxMessageDAO:
    @inject
    def __init__(self, engine: Engine):
        self._engine = engine

    def select_unsent(self) -> Iterable[OutboxMessage]:
        query = select([
            outbox_message_table.c.message_id,
            outbox_message_table.c.topic,
            outbox_message_table.c.type,
            outbox_message_table.c.body,
        ]).where(
            outbox_message_table.c.sent_at.is_(None)
        ).order_by(outbox_message_table.c.id)
        with self._engine.connect() as connection:
            records = connection.execute(query)
            return (OutboxMessage(*record) for record in records)

    def save(self, event: OutboxMessage):
        event_dict = dataclasses.asdict(event)
        statement = insert(outbox_message_table).values(**event_dict)
        with self._engine.connect() as connection:
            connection.execute(statement)

    def mark_as_sent(self, events: Iterable[OutboxMessage]):
        ids = [event.message_id for event in events]
        statement = update(outbox_message_table).where(
            outbox_message_table.c.message_id.in_(ids)
        ).values({outbox_message_table.c.sent_at: func.now()})
        with self._engine.connect() as connection:
            connection.execute(statement)

    def remove_sent(self):
        day_before = datetime.utcnow() - timedelta(days=1)
        statement = delete(outbox_message_table).where(outbox_message_table.c.sent_at <= day_before)
        with self._engine.connect() as connection:
            connection.execute(statement)
