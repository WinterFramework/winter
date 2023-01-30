import time
from threading import Event

from injector import inject

from .outbox_message_dao import OutboxMessageDAO
from ..rabbitmq.rabbitmq_client import RabbitMQClient
from ..rabbitmq.topology_configurator import TopologyConfig


class OutboxProcessor:

    @inject
    def __init__(
        self,
        rabbitmq_client: RabbitMQClient,
        outbox_message_doa: OutboxMessageDAO,
        config: TopologyConfig,
    ) -> None:
        self._rabbitmq_client = rabbitmq_client
        self._outbox_message_doa = outbox_message_doa
        self._topology_config = config

    def run(self, cancel_token: Event):
        time.sleep(1)

        while True:
            outbox_messages = self._outbox_message_doa.select_unsent()
            has_messages = False
            for index, outbox_message in enumerate(outbox_messages):
                has_messages = True
                exchange = self._topology_config.get_exchange_key(outbox_message.topic)
                self._rabbitmq_client.publish(outbox_message, exchange)
                self._outbox_message_doa.mark_as_sent([outbox_message])
                print('Message published ' + str(index))

            if cancel_token.is_set():
                break

            if not has_messages:
                time.sleep(1)
