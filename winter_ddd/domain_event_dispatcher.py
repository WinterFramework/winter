import warnings
from collections import defaultdict
from typing import Callable
from typing import Iterable
from typing import List
from typing import Type
from typing import TypeVar

from .domain_event_subscription import DomainEventSubscription
from .domain_event import DomainEvent

T = TypeVar('T')
HandlerFactory = Callable[[Type[T]], T]


class DomainEventDispatcher:
    def __init__(self):
        self._handlers = defaultdict(list)
        self._subscriptions = {}
        self._event_type_to_event_filter_map = {}
        self._handler_factory = lambda cls: cls()

    def set_handler_factory(self, handler_factory: HandlerFactory):
        self._handler_factory = handler_factory

    def add_subscription(self, subscription: DomainEventSubscription):
        self._subscriptions.setdefault(subscription.event_filter, []).append(subscription)
        for event_type in subscription.event_filter:
            self._event_type_to_event_filter_map.setdefault(event_type, []).append(subscription)

    def dispatch(self, domain_events: Iterable[DomainEvent]):
        domain_events_map = {}

        for domain_event in domain_events:
            domain_event_class = type(domain_event)
            typed_domain_events = domain_events_map.setdefault(domain_event_class, [])
            typed_domain_events.append(domain_event)

        for domain_event_class, typed_domain_events in domain_events_map.items():
            self._handle_events(domain_event_class, typed_domain_events)

    def _handle_events(self, domain_event_class: Type[DomainEvent], domain_events: List[DomainEvent]) -> None:
        if not domain_events:
            return None

        if List[domain_event_class] in self._handlers:
            for handler_cls, handler in self._handlers[List[domain_event_class]]:
                handler_instance = self._handler_factory(handler_cls)
                handler(handler_instance, domain_events)

        if domain_event_class not in self._handlers and List[domain_event_class] in self._handlers:
            warnings.warn(
                f'Unknown domain event {domain_event_class}. Please register at least one domain event handler')

        for handler_cls, handler in self._handlers[domain_event_class]:
            handler_instance = self._handler_factory(handler_cls)
            for domain_event in domain_events:
                handler(handler_instance, domain_event)
