from injector import inject
from pika import BasicProperties
from pika import DeliveryMode
from pika.exceptions import AMQPConnectionError
from pika.exceptions import NackError
from pika.exceptions import UnroutableError
from pika.exchange_type import ExchangeType
from retry import retry

from winter.web import MediaType
from winter_messaging_outbox_transacton.outbox.outbox_message import OutboxMessage
from winter_messaging_outbox_transacton.rabbitmq import create_connection
from winter_messaging_outbox_transacton.naming_convention import get_routing_key


class MessageNotPublishedException(Exception):
    pass


class RabbitMQClient:
    DLX = "winter.dead_letter_exchange"
    DLQ = "winter.dead_letter_queue"

    @inject
    def __init__(self) -> None:
        self._init_channel()

    def _init_channel(self):
        self._connection = create_connection()
        self._channel = self._connection.channel()
        self._channel.confirm_delivery()

    def declare_dead_letter(self):
        self._channel.exchange_declare(self.DLX, ExchangeType.direct.value, durable=True)
        result_queue = self._channel.queue_declare(self.DLQ, durable=True, arguments={"x-queue-type": "quorum"})
        self._channel.queue_bind(result_queue.method.queue, self.DLX, "*")

    @retry(AMQPConnectionError, delay=1)
    def publish(self, message: OutboxMessage, exchange: str, app_id: str):
        if self._connection.is_closed or self._channel.is_closed:
            self._init_channel()

        routing_key = get_routing_key(message.topic, message.type)
        properties = BasicProperties(
            app_id=app_id,
            type=message.type,
            message_id=str(message.id),
            content_type=str(MediaType.APPLICATION_JSON),
            delivery_mode=DeliveryMode.Persistent,
        )
        try:
            self._channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message.body,
                properties=properties,
                mandatory=True,
            )
        except (UnroutableError, NackError):
            err_message = f'Published failed. Message id: {message.id}; ' \
                          f'routing key: {routing_key}; exchange: {exchange}. ' \
                          f'Check configuration settings for confirmation'
            raise MessageNotPublishedException(err_message)

    def declare_exchange(self, exchange_name):
        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=ExchangeType.topic.value,
            durable=True,
        )

    def declare_queue(self, consumer_queue):
        arguments = {
            "x-queue-type": "quorum",
            "x-dead-letter-exchange": self.DLX,
            "x-dead-letter-strategy": "at-least-once",
            "x-overflow": "reject-publish",
        }
        return self._channel.queue_declare(consumer_queue, durable=True, arguments=arguments)

    def queue_bind(self, exchange, result, routing_key):
        self._channel.queue_bind(
            queue=result.method.queue,
            exchange=exchange,
            routing_key=routing_key,
        )

    @retry(AMQPConnectionError, delay=1, backoff=2)
    def start_consuming(self, queue, callback):
        if self._connection.is_closed or self._channel.is_closed:
            self._init_channel()

        self._channel.basic_consume(queue, callback)
        self._channel.start_consuming()

    def stop_consuming(self):
        self._channel.stop_consuming()

    def close(self):
        self._channel.close()
        self._connection.close()
