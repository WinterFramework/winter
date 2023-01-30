from injector import inject
from pika import BasicProperties
from pika import DeliveryMode
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import UnroutableError

from winter_messaging_outbox_transacton.outbox.outbox_message import OutboxMessage
from winter_messaging_outbox_transacton.utils import get_routing_key


class MessageNotPublishedException(Exception):
    pass


class RabbitMQClient:
    @inject
    def __init__(self, channel: BlockingChannel) -> None:
        self._channel = channel

    def publish(self, message: OutboxMessage, exchange):
        routing_key = get_routing_key(message.topic, message.type)
        try:
            properties = BasicProperties(
                app_id='producer',
                type=message.type,
                message_id=str(message.id),
                content_type='application/json',
                delivery_mode=DeliveryMode.Transient,
            )

            self._channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message.body,
                properties=properties,
                mandatory=True,
            )
        except UnroutableError:
            raise MessageNotPublishedException('Message could not be confirmed')
