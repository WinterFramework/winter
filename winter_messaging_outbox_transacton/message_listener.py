import json
import logging
from datetime import datetime
from uuid import UUID

from django.db import transaction
from injector import inject
from pika import BasicProperties
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from sqlalchemy.engine import Engine
from winter.core.json import json_decode
from winter.messaging import Event
from winter.messaging import EventHandlerRegistry
from winter.messaging.event_dispacher import EventDispatcher

from winter_messaging_outbox_transacton.exceptions import InterruptProcessException
from winter_messaging_outbox_transacton.inbox.inbox_message import InboxMessage
from winter_messaging_outbox_transacton.inbox.inbox_message_dao import InboxMessageDAO
from winter_messaging_outbox_transacton.retry_on_deadlock import retry_on_deadlock_decorator
from winter_messaging_outbox_transacton.signals import after_event_handling_signal
from winter_messaging_outbox_transacton.signals import before_event_handling_signal
from winter_messaging_outbox_transacton.timeout import TimeoutException
from winter_messaging_outbox_transacton.timeout import timeout

logger = logging.getLogger('event_handling')

EVENT_HANDLING_TIMEOUT = 15
RETRY_ON_DEADLOCK_ATTEMPTS = 1


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

            with self._engine.begin():
                self._dispatch_event(event)
                self._inbox_message_dao.mark_as_handled(inbox_message.id, self._consumer_id)

            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except TimeoutException:
            logger.error(f'Timeout Error is raised during handling event({message_id})')
            channel.basic_nack(delivery_tag=method_frame.delivery_tag)
        except InterruptProcessException:
            # TODO: what to do with the "is_new" check
            channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)
        except Exception as e:
            logger.error(f'Exception is raised during handling {message_id}: {e}')
            channel.basic_nack(delivery_tag=method_frame.delivery_tag)

    @retry_on_deadlock_decorator(RETRY_ON_DEADLOCK_ATTEMPTS)
    @timeout(EVENT_HANDLING_TIMEOUT)
    @transaction.atomic
    def _dispatch_event(self, event: Event):
        try:
            before_event_handling_signal.send()
            self._event_dispatcher.dispatch(event)
        finally:
            after_event_handling_signal.send()
