import dataclasses
from datetime import datetime
from typing import Iterable

from injector import inject
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.engine import Engine

from .outbox_message import OutboxMessage
from .outbox_message import outbox_message_table


class OutboxMessageDAO:
    table = outbox_message_table

    @inject
    def __init__(self, engine: Engine):
        self._engine = engine

    def select_unsent(self) -> Iterable[OutboxMessage]:
        query = select(
            outbox_message_table.c.id,
            outbox_message_table.c.topic,
            outbox_message_table.c.type,
            outbox_message_table.c.body,
            outbox_message_table.c.create_at,
            outbox_message_table.c.sent_at,
        ).where(outbox_message_table.c.sent_at.is_(None))
        with self._engine.connect() as connection:
            records = connection.execute(query)
            return (OutboxMessage(*record) for record in records)

    def save(self, event: OutboxMessage):
        statement = insert(self.table).values(**dataclasses.asdict(event))
        with self._engine.connect() as connection:
            connection.execute(statement)

    def mark_as_sent(self, events: Iterable[OutboxMessage]):
        ids = [event.id for event in events]
        statement = update(self.table).where(
            outbox_message_table.c.id.in_(ids)
        ).values({outbox_message_table.c.sent_at: datetime.now()})
        with self._engine.connect() as connection:
            connection.execute(statement)
