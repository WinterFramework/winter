import dataclasses
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
        query = select(
            outbox_message_table.c.id,
            outbox_message_table.c.topic,
            outbox_message_table.c.type,
            outbox_message_table.c.body,
            outbox_message_table.c.created_at,
            outbox_message_table.c.sent_at,
        ).where(outbox_message_table.c.sent_at.is_(None))
        with self._engine.connect() as connection:
            records = connection.execute(query)
            return (OutboxMessage(*record) for record in records)

    def save(self, event: OutboxMessage):
        event_dict = dataclasses.asdict(event)
        del event_dict['created_at']
        statement = insert(outbox_message_table).values(**event_dict)
        with self._engine.connect() as connection:
            connection.execute(statement)

    def mark_as_sent(self, events: Iterable[OutboxMessage]):
        ids = [event.id for event in events]
        statement = update(outbox_message_table).where(
            outbox_message_table.c.id.in_(ids)
        ).values({outbox_message_table.c.sent_at: func.now()})
        with self._engine.connect() as connection:
            connection.execute(statement)

    def remove_sent(self):
        statement = delete(outbox_message_table).where(outbox_message_table.c.sent_at.isnot_(None))
        with self._engine.connect() as connection:
            connection.execute(statement)
