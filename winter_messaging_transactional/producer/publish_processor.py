import logging
import signal
from threading import Event

from injector import inject
from sqlalchemy.orm import Session

from winter_messaging_transactional.rabbitmq import TopologyConfigurator
from winter_messaging_transactional.rabbitmq.rabbitmq_client import MessageNotPublishedException
from winter_messaging_transactional.rabbitmq.rabbitmq_client import RabbitMQClient
from winter_messaging_transactional.producer.outbox.outbox_message_dao import OutboxMessageDAO

log = logging.getLogger(__name__)


class PublishProcessor:
    @inject
    def __init__(
        self,
        rabbitmq_client: RabbitMQClient,
        outbox_message_doa: OutboxMessageDAO,
        configurator: TopologyConfigurator,
        session: Session,
        publish_interval: float = 1.0,
    ) -> None:
        self._rabbitmq_client = rabbitmq_client
        self._outbox_message_doa = outbox_message_doa
        self._topology_configurator = configurator
        self._publish_interval = publish_interval
        self._session = session

    def run(self):
        log.info('Publishing processor started with sleep time: %s', self._publish_interval)
        cancel_token = Event()

        def handle_interrupt_signal(signum, frame):
            cancel_token.set()

        signal.signal(signal.SIGTERM, handle_interrupt_signal)
        signal.signal(signal.SIGINT, handle_interrupt_signal)

        is_error_occurred = False
        while not cancel_token.wait(self._publish_interval):
            with self._session.begin():
                outbox_messages = self._outbox_message_doa.select_unsent()
                for outbox_message in outbox_messages:
                    exchange = self._topology_configurator.get_exchange_key(outbox_message.topic)
                    try:
                        self._rabbitmq_client.publish(outbox_message, exchange)
                        self._outbox_message_doa.mark_as_sent([outbox_message])
                    except MessageNotPublishedException:
                        log.exception('Publishing processor error. Message not published: %s', outbox_message.message_id)
                        is_error_occurred = True
                        break

                if is_error_occurred:
                    log.error('Publishing processor aborted due to an error')
                    break

                if cancel_token.is_set():
                    log.info('Publishing processor stopped')
                    break
