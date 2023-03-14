import logging
import signal

from injector import inject
from pika.exceptions import AMQPConnectionError
from retry import retry

from winter_messaging_outbox_transacton.rabbitmq import TopologyConfigurator
from winter_messaging_outbox_transacton.rabbitmq.message_listener import MessageListener
from winter_messaging_outbox_transacton.rabbitmq.rabbitmq_client import RabbitMQClient
from winter_messaging_outbox_transacton.timeout_handler import TimeoutHandler

logger = logging.getLogger(__name__)


class ConsumerWorker:
    @inject
    def __init__(
        self,
        configurator: TopologyConfigurator,
        message_listener: MessageListener,
        rabbit_client: RabbitMQClient,
    ) -> None:
        self._configurator = configurator
        self._message_listener = message_listener
        self._rabbit_client = rabbit_client
        self._timeout_handler = TimeoutHandler()

    def start(self, consumer_id: str):
        self._message_listener.set_consumer_id(consumer_id)
        self._message_listener.set_timeout_handler(self._timeout_handler)
        queue = self._configurator.get_consumer_queue(consumer_id)
        self._rabbit_client.start_consuming(queue, self._message_listener.on_message_callback)

        def handle_interrupt_signal(signum, frame):
            self._rabbit_client.stop_consuming()
            self._timeout_handler.can_retry = False

        signal.signal(signal.SIGTERM, handle_interrupt_signal)
        signal.signal(signal.SIGINT, handle_interrupt_signal)

        self._start_with_retry(consumer_id)

    @retry(AMQPConnectionError, delay=5, jitter=(1, 3))
    def _start_with_retry(self, consumer_id):
        try:
            self._rabbit_client.start_consuming()
        except Exception:
            logger.exception('Consumer worker %s stopping by Exception', consumer_id)
        finally:
            self._rabbit_client.stop_consuming()
        self._channel.connection.close()

