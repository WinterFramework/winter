import logging
import signal
from threading import Event

from injector import inject

from winter_messaging_transactional.consumer.inbox.inbox_message_dao import InboxMessageDAO

log = logging.getLogger(__name__)


class InboxCleanupProcessor:

    @inject
    def __init__(
        self,
        inbox_message_doa: InboxMessageDAO,
    ) -> None:
        self._inbox_message_doa = inbox_message_doa

    def run(self, cleanup_interval: float = 35):
        cancel_token = Event()

        def handle_interrupt_signal(signum, frame):
            cancel_token.set()

        signal.signal(signal.SIGTERM, handle_interrupt_signal)
        signal.signal(signal.SIGINT, handle_interrupt_signal)

        log.info('Cleanup inbox processor started with sleep time: %s', cleanup_interval)
        while not cancel_token.wait(cleanup_interval):
            self._inbox_message_doa.remove_handled()
