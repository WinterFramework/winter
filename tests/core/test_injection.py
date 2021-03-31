from injector import Injector

from winter.core import get_injector
from winter.core import set_injector


def test_set_get_injector():
    injector = Injector()
    set_injector(injector)
    assert get_injector() is injector
