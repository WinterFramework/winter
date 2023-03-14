from dataclasses import asdict

from injector import inject

from tests.winter_messaging.app_sample.producer import SampleProducerNotifyEvent
from winter.messaging import event_handler
from .consumer_dao import ConsumerDAO


class ConsumerCorrectEventHandler:
    @inject
    def __init__(self, consumer_dao: ConsumerDAO) -> None:
        self._consumer_dao = consumer_dao

    @event_handler
    def on_notify_event_handle_correct(self, event: SampleProducerNotifyEvent):
        print('ConsumerFirstEventHandler handle:', event)
        self._consumer_dao.save(**asdict(event))
