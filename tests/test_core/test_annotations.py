import dataclasses

from winter.core import Component
from winter.core import annotations
from winter.core import is_component


@dataclasses.dataclass(frozen=True)
class Route:
    path: str


def route(path: str):
    return annotations(Route(path))


def test_on_class():
    @route('test')
    class SimpleComponent:
        pass

    assert is_component(SimpleComponent)
    component = Component.get_by_cls(SimpleComponent)
    assert component.annotations.get(Route) == [Route('test')]


def test_on_method():
    class SimpleComponent:

        @route('test')
        def method(self):
            pass

    assert SimpleComponent.method.annotations.get(Route) == [Route('test')]
