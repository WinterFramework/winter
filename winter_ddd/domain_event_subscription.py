import inspect
from dataclasses import dataclass
from typing import Callable
from typing import Tuple
from typing import Type
from typing import get_args

from winter.core.utils.typing import is_iterable_type
from winter.core.utils.typing import is_union
from .domain_event import DomainEvent


@dataclass(frozen=True)
class DomainEventSubscription:
    event_filter: Tuple[Type[DomainEvent]]
    collection: bool
    handler_class: Type
    handler_method: Callable

    @staticmethod
    def create(handler_class, handler_method):
        func_spec = inspect.getfullargspec(handler_method)
        arg_type = func_spec.annotations[func_spec.args[1]]
        collection = is_iterable_type(arg_type)
        if collection:
            arg_type = get_args(arg_type)[0]
        if is_union(arg_type):
            domain_event_classes = tuple(get_args(arg_type))
        else:
            domain_event_classes = (arg_type, )
        return DomainEventSubscription(domain_event_classes, collection, handler_class, handler_method)
