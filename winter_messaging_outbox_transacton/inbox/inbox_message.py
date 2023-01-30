from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID

inbox_metadata = MetaData()


@dataclass
class InboxMessage:
    id: UUID
    consumer_id: str
    name: str
    received_at: datetime
    received_at: Optional[datetime]


inbox_message_table = sa.Table(
    'winter_inbox_message',
    inbox_metadata,
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
    sa.Column('consumer_id', postgresql.TEXT, nullable=False, primary_key=True),
    sa.Column('name', postgresql.TEXT, nullable=False),
    sa.Column('received_at', postgresql.DATE, nullable=False),
    sa.Column('processed_at', postgresql.DATE, nullable=True),
)
