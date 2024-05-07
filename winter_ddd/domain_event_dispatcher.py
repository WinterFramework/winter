from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Type

from winter.core import Component
from winter.core import ComponentMethod
from winter.core import get_injector
from winter.core.module_discovery import get_all_classes
from winter.core.module_discovery import import_recursively
from .domain_event import DomainEvent
from .domain_event_handler import DomainEventHandlerAnnotation
from .domain_event_subscription import DomainEventSubscription


class DomainEventDispatcher:
    def __init__(self):
        self.event_type_to_subscription_map: Dict[Type[DomainEvent], List[DomainEventSubscription]] = {}

    def add_handler(self, handler: ComponentMethod):
        subscription = DomainEventSubscription.create(handler.component.component_cls, handler.func)
        for event_type in subscription.event_filter:
            self.event_type_to_subscription_map.setdefault(event_type, []).append(subscription)

    def add_handlers_from_package(self, package_name: str):
        import_recursively(package_name)
        for class_name, class_ in get_all_classes(package_name):
            self.add_handlers_from_class(class_)

    def add_handlers_from_class(self, handler_class: Type):
        component = Component.get_by_cls(handler_class)
        for component_method in component.methods:
            if component_method.annotations.get_one_or_none(DomainEventHandlerAnnotation):
                self.add_handler(component_method)

    def dispatch(self, events: Iterable[DomainEvent]):
        events_grouped_by_subscription: Dict[DomainEventSubscription, List[DomainEvent]] = {}

        for event in events:
            event_type = type(event)
            domain_event_subscriptions = self.event_type_to_subscription_map.get(event_type, [])
            for domain_event_subscription in domain_event_subscriptions:
                events_grouped_by_subscription.setdefault(domain_event_subscription, []).append(event)

        injector = get_injector()

        for domain_event_subscription, events in events_grouped_by_subscription.items():
            handler_instance = injector.get(domain_event_subscription.handler_class)
            if domain_event_subscription.collection:
                self._execute_handler(domain_event_subscription.handler_method, handler_instance, events)
            else:
                for event in events:
                    self._execute_handler(domain_event_subscription.handler_method, handler_instance, event)

    def _execute_handler(self, func: Callable, *args, **kwargs):
        """
        The method is intentionally extracted to make it possible to override it externally for logging purposes.
        """
        func(*args, **kwargs)
