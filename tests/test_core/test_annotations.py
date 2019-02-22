import dataclasses
import pytest

from winter.core import Component
from winter.core import annotations
from winter.core import is_component
from winter.core.annotations import Annotations
from winter.core.annotations import NotFoundAnnotation
from winter.core.annotations import MultipleAnnotationFound


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


def test_get_one_not_found():

    annotations_ = Annotations()

    with pytest.raises(NotFoundAnnotation) as exception:
        annotations_.get_one(Route)

    assert exception.value.value_type == Route
    assert str(exception.value) == f'Not found annotation for {Route}'


def test_get_one_multiple_raises():

    annotations_ = Annotations()
    annotations_.add(Route('first'))
    annotations_.add(Route('second'))

    with pytest.raises(MultipleAnnotationFound) as exception:
        annotations_.get_one(Route)

    assert exception.value.value_type == Route
    assert str(exception.value) == f'Found more than one annotation for {Route}: 2'

def test_get_one():
    annotations_ = Annotations()
    annotations_.add(Route('first'))

    value = annotations_.get_one(Route)

    assert value == Route('first')
