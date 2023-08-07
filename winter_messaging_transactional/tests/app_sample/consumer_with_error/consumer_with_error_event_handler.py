from injector import inject

from winter_messaging_transactional.tests.app_sample.dao import ConsumerDAO
from winter_messaging_transactional.tests.app_sample.events import RetryableEvent
from winter.messaging import event_handler

ATTEMPTS_COUNT = 0


class ConsumerWithErrorEventHandler:

    @inject
    def __init__(self, consumer_dao: ConsumerDAO) -> None:
        self._consumer_dao = consumer_dao

    @event_handler
    def handle_event_raise_error(self, event: RetryableEvent):
        global ATTEMPTS_COUNT

        if event.can_be_handled_on_retry and ATTEMPTS_COUNT > 0:
            self._consumer_dao.save(id_=event.id, payload=event.payload)
            return

        ATTEMPTS_COUNT += 1
        raise Exception('Event handling error')
