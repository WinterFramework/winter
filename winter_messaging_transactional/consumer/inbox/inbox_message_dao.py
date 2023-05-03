import dataclasses
from datetime import datetime
from datetime import timedelta
from uuid import UUID

from injector import inject
from sqlalchemy import delete, and_
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import update
from sqlalchemy.engine import Engine

from .inbox_message import InboxMessage
from .inbox_message import inbox_message_table


@dataclasses.dataclass
class InboxResult:
    id: UUID
    counter: int
    processed_at: datetime


class InboxMessageDAO:

    @inject
    def __init__(self, engine: Engine):
        self._engine = engine

    def upsert(self, event: InboxMessage) -> InboxResult:
        inbox_event_dict = dataclasses.asdict(event)
        statement = insert(inbox_message_table).values(**inbox_event_dict).on_conflict_do_update(
            index_elements=[inbox_message_table.c.id, inbox_message_table.c.consumer_id],
            set_=dict(counter=inbox_message_table.c.counter + 1),
        ).returning(
            inbox_message_table.c.id,
            inbox_message_table.c.counter,
            inbox_message_table.c.processed_at,
        )
        with self._engine.connect() as connection:
            result = connection.execute(statement)
            inserted_record = result.fetchone()
            return InboxResult(*inserted_record)

    def mark_as_handled(self, id_: UUID, consumer_id: str):
        statement = update(inbox_message_table).where(
            and_(
                inbox_message_table.c.id == id_,
                inbox_message_table.c.consumer_id == consumer_id,
            )
        ).values(
            {inbox_message_table.c.processed_at: func.now()}
        )
        with self._engine.connect() as connection:
            connection.execute(statement)

    def remove_handled(self):
        day_before = datetime.utcnow() - timedelta(days=1)
        statement = delete(inbox_message_table).where(inbox_message_table.c.processed_at <= day_before)
        with self._engine.connect() as connection:
            connection.execute(statement)
