from injector import inject
from sqlalchemy.engine import Engine

from e2e.winter_messaging.app_sample.events import SampleEvent
from winter.messaging import event_handler
from e2e.winter_messaging.app_sample.dao import ConsumerDAO


class ConsumerCorrectEventHandler:
    @inject
    def __init__(self, consumer_dao: ConsumerDAO, engine: Engine) -> None:
        self._consumer_dao = consumer_dao
        self._engine = engine

    @event_handler
    def handle_event(self, event: SampleEvent):
        self._consumer_dao.save(id_=event.id + 1, payload=event.payload)
