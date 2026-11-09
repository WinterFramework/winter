from typing import Callable
from typing import Dict
from typing import List

from injector import Injector
from injector import inject

from .event import Event
from .event_subscription import EventSubscription
from .event_subscription_registry import EventSubscriptionRegistry


class EventDispatcher:
    @inject
    def __init__(self, subscription_registry: EventSubscriptionRegistry, injector: Injector) -> None:
        """The handlers of the events are created by the injector that creates the dispatcher."""
        self._subscription_registry = subscription_registry
        self._injector = injector

    def dispatch(self, event: Event):
        self.dispatch_many([event])

    def dispatch_many(self, events: List[Event]):
        events_grouped_by_subscription: Dict[EventSubscription, List[Event]] = {}
        for event in events:
            event_type = type(event)
            event_subscriptions = self._subscription_registry.get_subscriptions(event_type)

            for event_subscription in event_subscriptions:
                events_grouped_by_subscription.setdefault(event_subscription, []).append(event)

        for event_subscription, events in events_grouped_by_subscription.items():
            handler_instance = self._injector.get(event_subscription.handler_method.component.component_cls)

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
