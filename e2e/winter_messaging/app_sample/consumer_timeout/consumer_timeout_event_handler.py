import time

from injector import inject

from e2e.winter_messaging.app_sample.dao import ConsumerDAO
from e2e.winter_messaging.app_sample.events import SampleEvent
from winter.messaging import event_handler

ATTEMPTS_COUNT = 0


class ConsumerTimeoutEventHandler:
    @inject
    def __init__(self, consumer_dao: ConsumerDAO) -> None:
        self._consumer_dao = consumer_dao

    @event_handler
    def handle_event_timeout(self, event: SampleEvent):
        global ATTEMPTS_COUNT

        if not event.can_be_handled_on_retry or ATTEMPTS_COUNT == 0:
            ATTEMPTS_COUNT += 1
            time.sleep(20)

        self._consumer_dao.save(id_=event.id, payload=event.payload)
