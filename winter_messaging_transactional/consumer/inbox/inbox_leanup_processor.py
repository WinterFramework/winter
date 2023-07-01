import logging
from threading import Event

from injector import inject

from .inbox_message_dao import InboxMessageDAO

log = logging.getLogger(__name__)


class InboxCleanupProcessor:

    @inject
    def __init__(
        self,
        inbox_message_doa: InboxMessageDAO,
        cleanup_interval: float = 35
    ) -> None:
        self._inbox_message_doa = inbox_message_doa
        self._cleanup_interval = cleanup_interval

    def run(self, cancellation: Event):
        log.info('Cleanup inbox processor started with sleep time: %s', self._cleanup_interval)
        while not cancellation.wait(self._cleanup_interval):
            self._inbox_message_doa.remove_handled()

            if cancellation.is_set():
                log.info('Cleanup inbox processor stopped')
                break
