from typing import Dict
from typing import Iterable
from typing import List
from typing import Type

from winter.core import Component
from winter.core.module_discovery import get_all_classes
from winter.core.module_discovery import import_recursively
from .event import Event
from .event_handler import EventHandlerAnnotation
from .event_subscription import EventSubscription
from ..core import ComponentMethod


class EventSubscriptionRegistry:
    def __init__(self):
        self._event_type_to_subscription_map: Dict[Type[Event], List[EventSubscription]] = {}

    def register_subscription(self, handler_method: ComponentMethod):
        subscription = EventSubscription.create(handler_method)

        for event_type in subscription.event_filter:
            self._event_type_to_subscription_map.setdefault(event_type, []).append(subscription)

    def get_subscriptions(self, event_type: Type[Event]) -> Iterable[EventSubscription]:
        return self._event_type_to_subscription_map.get(event_type, [])

    def autodiscover(self, package_name: str):
        import_recursively(package_name)
        for class_name, class_ in get_all_classes(package_name):
            component = Component.get_by_cls(class_)
            for component_method in component.methods:
                if component_method.annotations.get_one_or_none(EventHandlerAnnotation):
                    self.register_subscription(component_method)
