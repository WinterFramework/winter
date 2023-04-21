import logging
from threading import Event

from injector import inject

from winter_messaging_transactional.rabbitmq import TopologyConfigurator
from winter_messaging_transactional.rabbitmq.rabbitmq_client import MessageNotPublishedException
from winter_messaging_transactional.rabbitmq.rabbitmq_client import RabbitMQClient
from winter_messaging_transactional.producer.outbox.outbox_message_dao import OutboxMessageDAO

log = logging.getLogger(__name__)


class PublishProcessor:
    SLEEP_TIME = 1.0

    @inject
    def __init__(
        self,
        rabbitmq_client: RabbitMQClient,
        outbox_message_doa: OutboxMessageDAO,
        configurator: TopologyConfigurator,
    ) -> None:
        self._rabbitmq_client = rabbitmq_client
        self._outbox_message_doa = outbox_message_doa
        self._topology_configurator = configurator

    def run(self, cancellation: Event, app_id: str):
        log.info('Publish processor started with sleep time: %s, app_id: %s', self.SLEEP_TIME, app_id)
        while not cancellation.wait(self.SLEEP_TIME):
            outbox_messages = self._outbox_message_doa.select_unsent()
            for index, outbox_message in enumerate(outbox_messages):
                exchange = self._topology_configurator.get_exchange_key(outbox_message.topic)
                try:
                    self._rabbitmq_client.publish(outbox_message, exchange, app_id)
                    self._outbox_message_doa.mark_as_sent([outbox_message])
                except MessageNotPublishedException:
                    log.exception('Publisher processor error. Message not published: %s', outbox_message.id)

            if cancellation.is_set():
                log.info('Publish processor stopped app_id: %s', app_id)
                break
