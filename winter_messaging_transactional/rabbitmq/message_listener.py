import json
import logging
from uuid import UUID

from injector import inject
from pika import BasicProperties
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from sqlalchemy.orm import Session

from winter.core.json import json_decode
from winter.messaging import Event
from winter.messaging import EventHandlerRegistry
from winter.messaging.event_dispacher import EventDispatcher
from winter_messaging_transactional.consumer.event_processing_logger import EventProcessingLogger
from winter_messaging_transactional.consumer.inbox.inbox_message import InboxMessage
from winter_messaging_transactional.consumer.inbox.inbox_message_dao import InboxMessageDAO
from winter_messaging_transactional.consumer.middleware_registry import MiddlewareRegistry
from winter_messaging_transactional.consumer.timeout_handler import TimeoutException
from winter_messaging_transactional.consumer.timeout_handler import TimeoutHandler

logger = logging.getLogger(__name__)

EVENT_HANDLING_TIMEOUT = 150
RETRIES_ON_TIMEOUT = 1


class MessageListener:
    MAX_RETRIES = 3

    @inject
    def __init__(
        self,
        handler_registry: EventHandlerRegistry,
        event_dispatcher: EventDispatcher,
        inbox_message_dao: InboxMessageDAO,
        middleware_registry: MiddlewareRegistry,
        session: Session,
    ) -> None:
        self._handler_registry = handler_registry
        self._event_dispatcher = event_dispatcher
        self._inbox_message_dao = inbox_message_dao
        self._middleware_registry = middleware_registry
        self._session = session
        self._timeout_handler = TimeoutHandler()
        timeout_decorator = self._timeout_handler.timeout(seconds=EVENT_HANDLING_TIMEOUT, retries=RETRIES_ON_TIMEOUT)
        self._dispatch_event = timeout_decorator(self._dispatch_event)
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
        message_id = UUID(properties.message_id)
        event_type_name = properties.type
        logger.info(f'Message(%s) is received with type: %s', message_id, event_type_name)
        inbox_message = InboxMessage(
            id=message_id,
            consumer_id=self._consumer_id,
            name=event_type_name,
        )
        result = self._inbox_message_dao.upsert(inbox_message)
        if result.processed_at is not None:
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        try:
            event_type = self._handler_registry.get_event_type(event_type_name)
            event_dict = json.loads(body)
            event = json_decode(event_dict, hint_class=event_type)
            self._dispatch_event(event=event, message_id=message_id)
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except TimeoutException:
            channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=False)
        except Exception:
            if result.counter < self.MAX_RETRIES:
                channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)
            else:
                logger.exception('Exception is raised during handling Message(%s)', message_id)
                channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=False)

    def _dispatch_event(self, event: Event, message_id: UUID):
        with EventProcessingLogger(message_id=message_id, event_type_name=event.__class__.__name__):
            with self._session.begin():
                self._middleware_registry.run_with_middlewares(lambda: self._event_dispatcher.dispatch(event))
                self._inbox_message_dao.mark_as_processed(message_id, self._consumer_id)

    def stop(self):
        self._timeout_handler.can_retry = False
