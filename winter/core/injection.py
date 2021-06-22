from typing import Optional
from typing import Type
from typing import TypeVar

import injector

_Interface = TypeVar('_Interface')


class Injector:
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._injector: injector.Injector = None

    def create_object(self, cls: Type[_Interface], additional_kwargs=None) -> _Interface:
        return self._get_injector().create_object(cls, additional_kwargs)

    def get(self, interface: Type[_Interface], scope=None) -> _Interface:
        return self._get_injector().get(interface, scope)

    def _get_injector(self) -> injector.Injector:
        if not self._injector:
            self._injector = injector.Injector(*self._args, **self._kwargs)
        return self._injector

    def __getattr__(self, item):
        return getattr(self._get_injector(), item)


_injector: Optional[Injector] = None


def set_injector(injector_: Injector) -> None:
    global _injector
    _injector = injector_


def get_injector() -> Injector:
    global _injector
    return _injector
