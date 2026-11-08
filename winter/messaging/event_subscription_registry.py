import types
from typing import Dict
from typing import Iterable
from typing import List
from typing import Sequence
from typing import Type

from winter.components import Component
from winter.application import find_definitions
from .event import Event
from .event_handler import EventHandlerAnnotation
from .event_subscription import EventSubscription
from winter.components import ComponentMethod


class EventSubscriptionRegistry:
    def __init__(self):
        self._event_type_to_subscription_map: Dict[Type[Event], List[EventSubscription]] = {}

    def register_subscription(self, handler_method: ComponentMethod):
        subscription = EventSubscription.create(handler_method)

        for event_type in subscription.event_filter:
            self._event_type_to_subscription_map.setdefault(event_type, []).append(subscription)

    def get_subscriptions(self, event_type: Type[Event]) -> Iterable[EventSubscription]:
        return self._event_type_to_subscription_map.get(event_type, [])

    def add_handlers_from_modules(self, modules: Sequence[types.ModuleType]):
        """Adds the handlers of the classes defined in the modules and their submodules, as WebApplication does."""
        definitions = find_definitions(modules)  # Importing the modules registers their components
        components = Component.get_all()
        for definition in definitions:
            if definition not in components:
                continue
            for component_method in components[definition].methods:
                if component_method.annotations.get_one_or_none(EventHandlerAnnotation):
                    self.register_subscription(component_method)
