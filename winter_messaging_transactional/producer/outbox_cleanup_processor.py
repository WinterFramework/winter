import logging
import signal
from threading import Event

from injector import inject

from winter_messaging_transactional.producer.outbox import OutboxMessageDAO

log = logging.getLogger(__name__)


class OutboxCleanupProcessor:
    @inject
    def __init__(
        self,
        outbox_message_doa: OutboxMessageDAO,
    ) -> None:
        self._outbox_message_doa = outbox_message_doa

    def run(self, cleanup_interval: float = 15.):
        cancel_token = Event()

        def handle_interrupt_signal(signum, frame):
            cancel_token.set()

        signal.signal(signal.SIGTERM, handle_interrupt_signal)
        signal.signal(signal.SIGINT, handle_interrupt_signal)

        log.info('Cleanup outbox processor started with sleep time: %s', cleanup_interval)
        while not cancel_token.wait(cleanup_interval):
            self._outbox_message_doa.remove_published()

            if cancel_token.is_set():
                log.info('Cleanup outbox processor stopped')
                break
