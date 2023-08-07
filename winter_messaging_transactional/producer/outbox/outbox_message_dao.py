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
from sqlalchemy.orm import Session

from .outbox_message import OutboxMessage
from .outbox_message import outbox_message_table


class OutboxMessageDAO:
    @inject
    def __init__(self, session: Session):
        self._session = session

    def select_unsent(self) -> Iterable[OutboxMessage]:
        query = select([
            outbox_message_table.c.message_id,
            outbox_message_table.c.topic,
            outbox_message_table.c.type,
            outbox_message_table.c.body,
        ]).where(
            outbox_message_table.c.published_at.is_(None)
        ).order_by(outbox_message_table.c.id)
        records = self._session.execute(query)
        return (OutboxMessage(*record) for record in records)

    def save(self, event: OutboxMessage):
        event_dict = dataclasses.asdict(event)
        statement = insert(outbox_message_table).values(**event_dict)
        self._session.execute(statement)

    def mark_as_sent(self, events: Iterable[OutboxMessage]):
        ids = [event.message_id for event in events]
        statement = update(outbox_message_table).where(
            outbox_message_table.c.message_id.in_(ids)
        ).values({outbox_message_table.c.published_at: func.now()})
        self._session.execute(statement)

    def remove_published(self):
        day_before = datetime.utcnow() - timedelta(days=1)
        statement = delete(outbox_message_table).where(outbox_message_table.c.published_at <= day_before)
        self._session.execute(statement)
