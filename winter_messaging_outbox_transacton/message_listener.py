import json
from datetime import datetime
from uuid import UUID

from injector import inject
from sqlalchemy.engine import Engine

from winter.core.json import json_decode
from winter.messaging import EventHandlerRegistry
from winter.messaging.event_dispacher import EventDispatcher
from winter_messaging_outbox_transacton.inbox.inbox_message import InboxMessage
from winter_messaging_outbox_transacton.inbox.inbox_message_dao import InboxMessageDAO


class MessageListener:
    @inject
    def __init__(
        self,
        handler_registry: EventHandlerRegistry,
        event_dispatcher: EventDispatcher,
        inbox_message_dao: InboxMessageDAO,
        engine: Engine,
    ) -> None:
        self._handler_registry = handler_registry
        self._event_dispatcher = event_dispatcher
        self._inbox_message_dao = inbox_message_dao
        self._engine = engine
        self.consumer_id = None

    def on_message_callback(self, channel, method_frame, properties, body):
        message_id = UUID(properties.message_id)
        event_type_name = properties.type
        if self._inbox_message_dao.exists_handled(message_id, self.consumer_id):
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        inbox_message = InboxMessage(
            id=message_id,
            consumer_id=self.consumer_id,
            name=event_type_name,
            # TODO date should be utc
            received_at=datetime.now(),
        )
        self._inbox_message_dao.save(inbox_message)

        event_type = self._handler_registry.get_event_type(event_type_name)
        event_dict = json.loads(body)
        event = json_decode(event_dict, hint_class=event_type)
        try:
            with self._engine.begin():
                self._event_dispatcher.dispatch(event)
                self._inbox_message_dao.mark_as_handled(inbox_message.id, self.consumer_id)

            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except Exception as ex:
            # TODO handle properly different use cases and add max timeout
            print(ex)
            channel.basic_nack(delivery_tag=method_frame.delivery_tag)
