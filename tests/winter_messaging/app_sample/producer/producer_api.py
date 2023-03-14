from dataclasses import asdict
from dataclasses import dataclass

from django.db import transaction
from injector import inject

import winter
from winter.messaging import EventPublisher
from .notify_event import SampleProducerNotifyEvent


@dataclass
class EventRequest:
    id: int
    name: str


@winter.route('sample-messaging/producer')
class SampleProducerAPI:
    @inject
    def __init__(self, event_publisher: EventPublisher):
        self._event_publisher = event_publisher

    @winter.route_post('/publish-event')
    @winter.request_body('event_request')
    def publish_event(self, event_request: EventRequest):
        event = SampleProducerNotifyEvent(**asdict(event_request))
        self._event_publisher.emit(event)

    @winter.route_post('/publish-event_with_error')
    @winter.request_body('event_request')
    def publish_event_with_error(self, event_request: EventRequest):
        with transaction.atomic():
            event = SampleProducerNotifyEvent(**asdict(event_request))
            self._event_publisher.emit(event)
            raise ValueError('test')