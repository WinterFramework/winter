from dataclasses import dataclass

from winter.messaging import Event
from winter.messaging import topic

from winter_messaging_transactional.tests.app_sample.events import SampleEvent
from winter.messaging import event_handler


@topic('not-declared-topic')
@dataclass(frozen=True)
class TopicEvent(Event):
    name: str


class SimpleEventHandler:

    @event_handler
    def handle_topic_event(self, event: TopicEvent):
        pass
