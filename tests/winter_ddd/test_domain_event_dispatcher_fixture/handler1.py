from winter_ddd import domain_event_handler
from .events import DomainEvent1


class Handler1:
    received_events = []

    @domain_event_handler
    def handle_event(self, event: DomainEvent1):
        self.received_events.append(event)
