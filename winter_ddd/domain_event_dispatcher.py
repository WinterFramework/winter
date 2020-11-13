from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Tuple
from typing import Type
from typing import TypeVar

from .domain_event import DomainEvent
from .domain_event_subscription import DomainEventSubscription

T = TypeVar('T')
HandlerFactory = Callable[[Type[T]], T]

EventFilter = Tuple[Type[DomainEvent]]


class DomainEventDispatcher:
    def __init__(self):
        self._subscriptions: Dict[EventFilter, List[DomainEventSubscription]] = {}
        self._event_type_to_event_filters_map: Dict[Type[DomainEvent], List[EventFilter]] = {}
        self._handler_factory = lambda cls: cls()

    def set_handler_factory(self, handler_factory: HandlerFactory):
        self._handler_factory = handler_factory

    def add_subscription(self, subscription: DomainEventSubscription):
        self._subscriptions.setdefault(subscription.event_filter, []).append(subscription)
        for event_type in subscription.event_filter:
            event_filters = self._event_type_to_event_filters_map.setdefault(event_type, [])
            if subscription.event_filter not in event_filters:
                event_filters.append(subscription.event_filter)

    def dispatch(self, events: Iterable[DomainEvent]):
        filtered_events: Dict[EventFilter, List[DomainEvent]] = {}

        for event in events:
            event_type = type(event)
            event_filters = self._event_type_to_event_filters_map.get(event_type, [])
            for event_filter in event_filters:
                filtered_events.setdefault(event_filter, []).append(event)

        for event_filter, events in filtered_events.items():
            for subscription in self._subscriptions.get(event_filter, []):
                handler_instance = self._handler_factory(subscription.handler_class)
                if subscription.collection:
                    subscription.handler_method(handler_instance, events)
                else:
                    for event in events:
                        subscription.handler_method(handler_instance, event)
