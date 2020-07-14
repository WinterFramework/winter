import inspect
import re
import warnings
from collections import defaultdict
from threading import Lock
from typing import Callable
from typing import Iterable
from typing import List
from typing import Type
from typing import TypeVar

from .domain_event import DomainEvent

T = TypeVar('T')

_instance_getter: Callable[[Type[T]], T] = lambda cls: cls()
_domain_event_handlers = defaultdict(list)

domain_events_class_name_pattern = re.compile(r'typing.List\[.+\]')


# noinspection PyPep8Naming
class domain_event_handler:
    """Decorator for method in class"""

    def __init__(self, method):
        self._method = method
        func_spec = inspect.getfullargspec(self._method)

        if len(func_spec.args) != 2:  # One argument and self
            raise AssertionError(f'Method must have only 1 arguments: {method.__qualname__}.')
        arg_type = func_spec.annotations[func_spec.args[1]]
        if (
            not inspect.isclass(arg_type) and
            not domain_events_class_name_pattern.match(str(arg_type))
        ):
            raise AssertionError('First argument must have annotation and this annotation must be class')
        self._domain_event_class = arg_type

    def __get__(self, instance, owner):
        return self._method.__get__(instance, owner)

    def __set_name__(self, owner, name):
        with Lock():
            _domain_event_handlers[self._domain_event_class].append((owner, self._method))


def process_domain_events(domain_events: Iterable[DomainEvent]):
    domain_events_map = {}

    for domain_event in domain_events:
        domain_event_class = type(domain_event)
        typed_domain_events = domain_events_map.setdefault(domain_event_class, [])
        typed_domain_events.append(domain_event)

    for domain_event_class, typed_domain_events in domain_events_map.items():
        _handle_domain_events(domain_event_class, typed_domain_events)


def _handle_domain_events(domain_event_class: Type[DomainEvent], domain_events: List[DomainEvent]) -> None:
    if not domain_events:
        return None

    if List[domain_event_class] in _domain_event_handlers:
        for handler_cls, handler in _domain_event_handlers[List[domain_event_class]]:
            handler_instance = _instance_getter(handler_cls)
            handler(handler_instance, domain_events)

    if domain_event_class not in _domain_event_handlers and List[domain_event_class] in _domain_event_handlers:
        warnings.warn(f'Unknown domain event {domain_event_class}. Please register at least one domain event handler')

    for handler_cls, handler in _domain_event_handlers[domain_event_class]:
        handler_instance = _instance_getter(handler_cls)
        for domain_event in domain_events:
            handler(handler_instance, domain_event)


def delete_domain_event_handler(cls):
    with Lock():
        del _domain_event_handlers[cls]


def get_instance_getter():
    return _instance_getter


def set_instance_getter(func: Callable[[Type[T]], T]):
    global _instance_getter
    _instance_getter = func
