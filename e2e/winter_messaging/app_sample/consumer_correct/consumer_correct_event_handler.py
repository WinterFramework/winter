from injector import inject
from sqlalchemy.orm import Session

from e2e.winter_messaging.app_sample.events import SampleEvent
from winter.messaging import event_handler
from e2e.winter_messaging.app_sample.dao import ConsumerDAO


class ConsumerCorrectEventHandler:
    @inject
    def __init__(
        self,
        consumer_dao: ConsumerDAO,
        session: Session,
    ) -> None:
        self._consumer_dao = consumer_dao
        self._session = session

    @event_handler
    def handle_event(self, event: SampleEvent):
        self._consumer_dao.save(id_=event.id, payload=event.payload)
