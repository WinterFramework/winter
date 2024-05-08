from winter_ddd import domain_event_handler
from ..events import DomainEvent2


class Handler2:
    received_events = []

    @domain_event_handler
    def handle_event(self, event: DomainEvent2):
        self.received_events.append(event)

    def intentionally_without_annotation(self, event: DomainEvent2):  # pragma: no cover
        # This shouldn't happen
        self.received_events.append(event)
