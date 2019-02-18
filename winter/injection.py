import warnings
from typing import Iterable
from typing import Optional
from typing import Union

from injector import Injector
from injector import Module

_injector = None


def set_injector(injector: Injector):
    warnings.warn('deprecated', DeprecationWarning)
    global _injector
    _injector = injector


def get_injector() -> Optional[Injector]:
    return _injector


def setup_injector(configuration: Optional[Union[Module, Iterable[Module]]] = None):
    global _injector
    _injector = Injector(modules=configuration)
    return _injector
