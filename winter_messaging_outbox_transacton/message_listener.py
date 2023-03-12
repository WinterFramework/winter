import json
import logging
from datetime import datetime
from uuid import UUID

from injector import inject
from pika import BasicProperties
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from sqlalchemy.engine import Engine
from winter.core.json import json_decode
from winter.messaging import Event
from winter.messaging import EventHandlerRegistry
from winter.messaging.event_dispacher import EventDispatcher
from winter_messaging_outbox_transacton.event_processing_logger import EventProcessingLogger
from winter_messaging_outbox_transacton.inbox.inbox_message import InboxMessage
from winter_messaging_outbox_transacton.inbox.inbox_message_dao import InboxMessageDAO
from winter_messaging_outbox_transacton.middleware_registry import MiddlewareRegistry
from winter_messaging_outbox_transacton.timeout_handler import TimeoutHandler

logger = logging.getLogger('event_handling')

EVENT_HANDLING_TIMEOUT = 15
RETRIES_ON_TIMEOUT = 1


class MessageListener:
    @inject
    def __init__(
        self,
        handler_registry: EventHandlerRegistry,
        event_dispatcher: EventDispatcher,
        inbox_message_dao: InboxMessageDAO,
        middleware_registry: MiddlewareRegistry,
        engine: Engine,
    ) -> None:
        self._handler_registry = handler_registry
        self._event_dispatcher = event_dispatcher
        self._inbox_message_dao = inbox_message_dao
        self._middleware_registry = middleware_registry
        self._engine = engine

        self._consumer_id = None

    def set_consumer_id(self, consumer_id: str):
        self._consumer_id = consumer_id

    def on_message_callback(
        self,
        channel: BlockingChannel,
        method_frame: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        try:
            message_id = UUID(properties.message_id)
            logger.info(f'Message({message_id}) is received')
            event_type_name = properties.type
            inbox_message = InboxMessage(
                id=message_id,
                consumer_id=self._consumer_id,
                name=event_type_name,
                # TODO date should be utc
                received_at=datetime.now(),
            )
            is_new = self._inbox_message_dao.save_if_not_exists(inbox_message)
            if not is_new:
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return

            event_type = self._handler_registry.get_event_type(event_type_name)
            event_dict = json.loads(body)
            event = json_decode(event_dict, hint_class=event_type)

            with EventProcessingLogger(message_id=message_id, event_type_name=event_type_name):
                self._dispatch_event(event=event, message_id=message_id)
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except Exception:
            logger.exception(f'Exception is raised during handling {message_id}')
            channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=False)

    @TimeoutHandler.timeout(seconds=EVENT_HANDLING_TIMEOUT, retries=RETRIES_ON_TIMEOUT)
    def _dispatch_event(self, event: Event, message_id: UUID):
        with self._engine.begin():
            self._middleware_registry.run_with_middlewares(lambda: self._event_dispatcher.dispatch(event))
            self._inbox_message_dao.mark_as_handled(message_id, self._consumer_id)
