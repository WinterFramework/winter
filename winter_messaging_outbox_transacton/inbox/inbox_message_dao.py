import dataclasses
from datetime import datetime
from uuid import UUID

from injector import inject
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import update
from sqlalchemy.engine import Engine

from .inbox_message import InboxMessage
from .inbox_message import inbox_message_table


class InboxMessageDAO:
    table = inbox_message_table

    @inject
    def __init__(self, engine: Engine):
        self._engine = engine

    def save_if_not_exists(self, event: InboxMessage) -> bool:
        statement = insert(self.table).values(
            **dataclasses.asdict(event)
        ).on_conflict_do_nothing(
            index_elements=[self.table.c.id, self.table.c.consumer_id]
        ).returning(self.table.c.id)
        with self._engine.connect() as connection:
            result = connection.execute(statement)
            inserted_record = result.fetchone()
            return inserted_record is not None

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
