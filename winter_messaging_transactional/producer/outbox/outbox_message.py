from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects import postgresql

from winter_messaging_transactional.table_metadata import messaging_metadata


@dataclass
class OutboxMessage:
    message_id: UUID
    topic: str
    type: str
    body: str


outbox_message_table = sa.Table(
    'winter_outbox_message',
    messaging_metadata,
    sa.Column('id', sa.INTEGER, nullable=False, primary_key=True, autoincrement=True),
    sa.Column('message_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
    sa.Column('topic', sa.TEXT, nullable=False),
    sa.Column('type', sa.TEXT, nullable=False),
    sa.Column('body', sa.TEXT, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=func.now()),
    sa.Column('published_at', sa.TIMESTAMP, nullable=True, index=True),
)
