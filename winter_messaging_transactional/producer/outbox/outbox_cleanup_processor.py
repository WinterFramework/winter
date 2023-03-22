import logging
from threading import Event

from injector import inject

from .outbox_message_dao import OutboxMessageDAO


log = logging.getLogger(__name__)


class OutboxCleanupProcessor:
    SLEEP_TIME = 15.0

    @inject
    def __init__(
        self,
        outbox_message_doa: OutboxMessageDAO,
    ) -> None:
        self._outbox_message_doa = outbox_message_doa

    def run(self, cancellation: Event):
        log.info('Cleanup outbox processor started with sleep time: %s', self.SLEEP_TIME)
        while not cancellation.wait(self.SLEEP_TIME):
            self._outbox_message_doa.remove_sent()

            if cancellation.is_set():
                log.info('Cleanup outbox processor stopped')
                break
