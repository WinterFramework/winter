from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID

outbox_metadata = MetaData()


@dataclass
class OutboxMessage:
    id: UUID
    topic: str
    type: str
    body: str
    created_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None


outbox_message_table = sa.Table(
    'winter_outbox_message',
    outbox_metadata,
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
    sa.Column('topic', sa.TEXT, nullable=False),
    sa.Column('type', sa.TEXT, nullable=False),
    sa.Column('body', sa.TEXT, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=func.now()),
    sa.Column('sent_at', sa.TIMESTAMP, nullable=True),
)
