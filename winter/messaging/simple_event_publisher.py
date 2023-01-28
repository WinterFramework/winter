from injector import inject

from .event import Event
from .event_dispacher import EventDispatcher
from .event_publisher import EventPublisher


class SimpleEventPublisher(EventPublisher):
    @inject
    def __init__(self, event_dispatcher: EventDispatcher):
        self._event_dispatcher = event_dispatcher

    def emit(self, event: Event):
        self._event_dispatcher.dispatch(event)
