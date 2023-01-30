import dataclasses
from datetime import datetime
from uuid import UUID

from injector import inject
from sqlalchemy import exists
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.engine import Engine

from .inbox_message import InboxMessage
from .inbox_message import inbox_message_table


class InboxMessageDAO:
    table = inbox_message_table

    @inject
    def __init__(self, engine: Engine):
        self._engine = engine

    def exists_handled(self, id_: UUID, consumer_id: str) -> bool:
        query = select(exists().where(
            inbox_message_table.c.id == id_,
            inbox_message_table.c.consumer_id == consumer_id,
            inbox_message_table.c.processed_at.is_not(None),
        ))
        with self._engine.connect() as connection:
            result = connection.execute(query)
            return next(result)[0]

    def save(self, event: InboxMessage):
        # TODO UPSERT ??
        statement = insert(self.table).values(**dataclasses.asdict(event))
        with self._engine.connect() as connection:
            connection.execute(statement)

    def mark_as_handled(self, id_: UUID, consumer_id: str):
        statement = update(self.table).where(
            inbox_message_table.c.id == id_,
            inbox_message_table.c.consumer_id == consumer_id,
        ).values(
            # TODO time in utc
            {inbox_message_table.c.processed_at: datetime.now()}
        )
        with self._engine.connect() as connection:
            connection.execute(statement)
