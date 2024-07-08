import inspect
from dataclasses import dataclass
from typing import Callable
from typing import Tuple
from typing import Type
from typing import get_args

from winter.core import ComponentMethod
from winter.core.utils.typing import is_iterable_type
from winter.core.utils.typing import is_union
from winter.messaging import Event


@dataclass(frozen=True)
class EventSubscription:
    event_filter: Tuple[Type[Event]]
    collection: bool
    handler_method: ComponentMethod

    @staticmethod
    def create(handler_method: ComponentMethod):
        arg_type = handler_method.arguments[0].type_
        collection = is_iterable_type(arg_type)

        if collection:
            arg_type = get_args(arg_type)[0]

        if is_union(arg_type):
            domain_event_classes = tuple(get_args(arg_type))
        else:
            domain_event_classes = (arg_type, )

        return EventSubscription(domain_event_classes, collection, handler_method)
