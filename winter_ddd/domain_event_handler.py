import inspect
import re

from .domain_event_subscription import DomainEventSubscription
from .domain_event_dispatcher import DomainEventDispatcher

domain_events_class_name_pattern = re.compile(r'typing.List\[.+\]')


global_domain_event_dispatcher = DomainEventDispatcher()


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
        self._arg_type = arg_type

    def __get__(self, instance, owner):
        return self._method.__get__(instance, owner)

    def __set_name__(self, owner, name):
        subscription = DomainEventSubscription.create(owner, self._method)
        global_domain_event_dispatcher.add_subscription(subscription)
