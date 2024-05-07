from typing import Callable
from typing import Dict
from typing import List

from injector import inject

from winter.core import get_injector
from .event import Event
from .event_subscription import EventSubscription
from .event_subscription_registry import EventSubscriptionRegistry


class EventDispatcher:
    @inject
    def __init__(self, subscription_registry: EventSubscriptionRegistry) -> None:
        self._subscription_registry = subscription_registry

    def dispatch(self, event: Event):
        self.dispatch_many([event])

    def dispatch_many(self, events: List[Event]):
        events_grouped_by_subscription: Dict[EventSubscription, List[Event]] = {}
        injector = get_injector()

        for event in events:
            event_type = type(event)
            event_subscriptions = self._subscription_registry.get_subscriptions(event_type)

            for event_subscription in event_subscriptions:
                events_grouped_by_subscription.setdefault(event_subscription, []).append(event)

        for event_subscription, events in events_grouped_by_subscription.items():
            handler_instance = injector.get(event_subscription.handler_method.component.component_cls)

            if event_subscription.collection:
                self._execute_handler(event_subscription.handler_method.func, handler_instance, events)
            else:
                for event in events:
                    self._execute_handler(event_subscription.handler_method.func, handler_instance, event)

    def _execute_handler(self, func: Callable, *args, **kwargs):
        """
        The method is intentionally extracted to make it possible to override it externally for logging purposes.
        """
        func(*args, **kwargs)
