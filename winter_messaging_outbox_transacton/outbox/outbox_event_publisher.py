import dataclasses
import json
from datetime import datetime
from uuid import uuid4

from injector import inject

from winter.core.json import JSONEncoder
from winter.messaging import Event
from winter.messaging import EventPublisher
from winter.messaging import get_event_topic
from .outbox_message import OutboxMessage
from .outbox_message_dao import OutboxMessageDAO


class OutboxEventPublisher(EventPublisher):
    @inject
    def __init__(self, outbox_message_doa: OutboxMessageDAO):
        self._outbox_message_dao = outbox_message_doa

    def emit(self, event: Event):
        event_type = type(event)
        topic_info = get_event_topic(event_type)
        event_dict = dataclasses.asdict(event)
        body = json.dumps(event_dict, ensure_ascii=False, cls=JSONEncoder)
        outbox_message = OutboxMessage(
            id=uuid4(),
            topic=topic_info.name,
            type=topic_info.event_name,
            body=body,
        )
        self._outbox_message_dao.save(outbox_message)
