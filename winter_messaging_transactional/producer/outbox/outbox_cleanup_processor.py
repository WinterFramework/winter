import logging
from threading import Event

from injector import inject

from .outbox_message_dao import OutboxMessageDAO


log = logging.getLogger(__name__)


class OutboxCleanupProcessor:
    @inject
    def __init__(
        self,
        outbox_message_doa: OutboxMessageDAO,
        cleanup_interval: float = 15.,
    ) -> None:
        self._outbox_message_doa = outbox_message_doa
        self._cleanup_interval = cleanup_interval

    def run(self, cancellation: Event):
        log.info('Cleanup outbox processor started with sleep time: %s', self._cleanup_interval)
        while not cancellation.wait(self._cleanup_interval):
            self._outbox_message_doa.remove_sent()

            if cancellation.is_set():
                log.info('Cleanup outbox processor stopped')
                break
