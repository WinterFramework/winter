from typing import Optional

from injector import Injector

_injector = None


def set_injector(injector: Injector):
    global _injector
    _injector = injector


def get_injector() -> Optional[Injector]:
    return _injector
