from injector import inject

from winter_messaging_transactional.tests.app_sample.events import SampleEvent
from winter.messaging import event_handler
from winter_messaging_transactional.tests.app_sample.dao import ConsumerDAO


class ConsumerCorrectEventHandler:
    @inject
    def __init__(self, consumer_dao: ConsumerDAO) -> None:
        self._consumer_dao = consumer_dao

    @event_handler
    def handle_event(self, event: SampleEvent):
        self._consumer_dao.save(id_=event.id + 1, payload=event.payload)
