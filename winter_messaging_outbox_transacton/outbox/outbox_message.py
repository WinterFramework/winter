from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID

outbox_metadata = MetaData()


@dataclass
class OutboxMessage:
    id: UUID
    topic: str
    type: str
    body: str
    create_at: datetime
    sent_at: Optional[datetime] = None


outbox_message_table = sa.Table(
    'winter_outbox_message',
    outbox_metadata,
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
    sa.Column('topic', postgresql.TEXT, nullable=False),
    sa.Column('type', postgresql.TEXT, nullable=False),
    sa.Column('body', postgresql.TEXT, nullable=False),
    sa.Column('create_at', postgresql.DATE, nullable=False),
    sa.Column('sent_at', postgresql.DATE, nullable=True),
)
