import logging
import signal

from injector import inject

from winter.messaging import EventHandlerRegistry
from winter.messaging import MessagingConfig
from winter_messaging_transactional.rabbitmq import TopologyConfigurator
from winter_messaging_transactional.rabbitmq.message_listener import MessageListener
from winter_messaging_transactional.rabbitmq.rabbitmq_client import RabbitMQClient

logger = logging.getLogger(__name__)


class ConsumerWorker:
    @inject
    def __init__(
        self,
        configurator: TopologyConfigurator,
        message_listener: MessageListener,
        rabbit_client: RabbitMQClient,
        handler_registry: EventHandlerRegistry,
        config: MessagingConfig
    ) -> None:
        self._configurator = configurator
        self._message_listener = message_listener
        self._rabbit_client = rabbit_client
        self._is_interrupted = False
        self._handler_registry = handler_registry
        self._config = config

    def start(self, consumer_id: str):
        logger.info(f'Starting message consumer id: %s', consumer_id)
        self._message_listener.set_consumer_id(consumer_id)
        self._discover_consumer_event_handlers(consumer_id)

        def handle_interrupt_signal(signum, frame):
            self._is_interrupted = True
            self._message_listener.stop()
            self._rabbit_client.stop_consuming()

        signal.signal(signal.SIGTERM, handle_interrupt_signal)
        signal.signal(signal.SIGINT, handle_interrupt_signal)

        queue = self._configurator.get_consumer_queue(consumer_id)
        try:
            self._rabbit_client.start_consuming(queue, self._message_listener.on_message_callback)
        except Exception:
            logger.exception('Consumer worker %s stopping by error', consumer_id)
            raise
        finally:
            if not self._is_interrupted:
                self._rabbit_client.stop_consuming()
            self._rabbit_client.close()

    def _discover_consumer_event_handlers(self, consumer_id: str):
        packages = self._config.consumers[consumer_id]
        for package_name in packages:
            self._handler_registry.autodiscover(consumer_id, package_name)
