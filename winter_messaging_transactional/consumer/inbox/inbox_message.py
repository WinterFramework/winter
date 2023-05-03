from dataclasses import dataclass

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID

from winter_messaging_transactional.table_metadata import messaging_metadata


@dataclass
class InboxMessage:
    id: UUID
    consumer_id: str
    name: str


inbox_message_table = sa.Table(
    'winter_inbox_message',
    messaging_metadata,
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
    sa.Column('consumer_id', postgresql.TEXT, nullable=False, primary_key=True),
    sa.Column('name', postgresql.TEXT, nullable=False),
    sa.Column('counter', postgresql.INTEGER, nullable=False, server_default='0'),
    sa.Column('received_at', sa.TIMESTAMP, nullable=False, server_default=func.now()),
    sa.Column('processed_at', sa.TIMESTAMP, nullable=True, index=True),
)
