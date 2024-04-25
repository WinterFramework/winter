from typing import Dict
from typing import Iterable
from typing import List
from typing import Type

from winter.core import get_injector
from .domain_event import DomainEvent
from .domain_event_subscription import DomainEventSubscription


class DomainEventDispatcher:
    def __init__(self):
        self.event_type_to_subscription_map: Dict[Type[DomainEvent], List[DomainEventSubscription]] = {}

    def add_subscription(self, subscription: DomainEventSubscription):
        for event_type in subscription.event_filter:
            self.event_type_to_subscription_map.setdefault(event_type, []).append(subscription)

    def dispatch(self, events: Iterable[DomainEvent]):
        events_grouped_by_subscription_key: Dict[str, List[DomainEvent]] = {}
        subscriptions_map: Dict[str, DomainEventSubscription] = {}

        for event in events:
            event_type = type(event)
            domain_event_subscriptions = self.event_type_to_subscription_map.get(event_type, [])
            for domain_event_subscription in domain_event_subscriptions:
                # subscription_key is used to group events by subscription
                # in case when handler methods in event_type_to_subscription_map will be decorated
                subscription_key = (
                    f'{domain_event_subscription.handler_class.__module__}.'
                    f'{domain_event_subscription.handler_class.__name__}.'
                    f'{domain_event_subscription.handler_method.__name__}'
                )
                events_grouped_by_subscription_key.setdefault(subscription_key, []).append(event)
                subscriptions_map[subscription_key] = domain_event_subscription

        injector = get_injector()

        for subscription_key, events in events_grouped_by_subscription_key.items():
            domain_event_subscription = subscriptions_map[subscription_key]
            handler_instance = injector.get(domain_event_subscription.handler_class)
            if domain_event_subscription.collection:
                domain_event_subscription.handler_method(handler_instance, events)
            else:
                for event in events:
                    domain_event_subscription.handler_method(handler_instance, event)


global_domain_event_dispatcher = DomainEventDispatcher()
