from typing import Optional

from injector import Injector

_injector: Optional[Injector] = None


def set_injector(injector: Injector) -> None:
    global _injector
    _injector = injector


def get_injector() -> Injector:
    global _injector
    return _injector
