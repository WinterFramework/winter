from .domain_events import DomainEvents


class AggregateRoot:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._domain_events: DomainEvents = None

    @property
    def domain_events(self) -> DomainEvents:
        if getattr(self, '_domain_events', None) is None:
            self._domain_events = DomainEvents()
        return self._domain_events

    def clear_domain_events(self):
        self._domain_events.clear()
