import logging
from threading import Event

from injector import inject

from .inbox_message_dao import InboxMessageDAO

log = logging.getLogger(__name__)


class InboxCleanupProcessor:
    SLEEP_TIME = 35.0

    @inject
    def __init__(
        self,
        inbox_message_doa: InboxMessageDAO,
    ) -> None:
        self._inbox_message_doa = inbox_message_doa

    def run(self, cancellation: Event):
        log.info('Cleanup inbox processor started with sleep time: %s', self.SLEEP_TIME)
        while not cancellation.wait(self.SLEEP_TIME):
            self._inbox_message_doa.remove_handled()

            if cancellation.is_set():
                log.info('Cleanup inbox processor stopped')
                break
