import signal
from injector import inject
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError
from retry import retry
from winter.messaging import EventHandlerRegistry
from winter_messaging_outbox_transacton.message_listener import MessageListener
from winter_messaging_outbox_transacton.rabbitmq import TopologyConfigurator


class ConsumerWorker:
    @inject
    def __init__(
        self,
        event_handler_registry: EventHandlerRegistry,
        configurator: TopologyConfigurator,
        message_listener: MessageListener,
        channel: BlockingChannel,
    ) -> None:
        self._event_handler_registry = event_handler_registry
        self._configurator = configurator
        self._message_listener = message_listener
        self._channel = channel

    def start(self, consumer_id: str, package_name: str):
        self._message_listener.set_consumer_id(consumer_id)
        self._configurator.autodiscover(package_name)
        configuration = self._configurator.configure_topics()
        self._configurator.configure_listener(
            consumer_id,
            configuration,
            self._message_listener.on_message_callback,
        )

        def handle_interrupt_signal(signum, frame):
            self._channel.stop_consuming()

        signal.signal(signal.SIGTERM, handle_interrupt_signal)
        signal.signal(signal.SIGINT, handle_interrupt_signal)

        self._start_with_retry(consumer_id)

    @retry(AMQPConnectionError, delay=5, jitter=(1, 3))
    def _start_with_retry(self, consumer_id):
        # TODO add reconnect method
        try:
            self._channel.start_consuming()
        except Exception as e:
            print(f'Consumer worker {consumer_id} stopping by Exception: {e}')
        finally:
            self._channel.stop_consuming()
        self._channel.connection.close()

