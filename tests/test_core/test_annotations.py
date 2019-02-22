import dataclasses
import pytest

from winter.core import Component
from winter.core import annotate
from winter.core import annotate_class
from winter.core import annotate_method
from winter.core import is_component
from winter.core.annotations import Annotations
from winter.core.annotations import MultipleAnnotationFound
from winter.core.annotations import NotFoundAnnotation


@dataclasses.dataclass(frozen=True)
class Route:
    path: str


def route(path: str):
    return annotate(Route(path))


def route_class(path: str):
    return annotate_class(Route(path))


def route_method(path: str):
    return annotate_method(Route(path))



@pytest.mark.parametrize('decorator', (route, route_class))
def test_on_class_by_decorator(decorator):

    @decorator('test')
    class SimpleComponent:
        pass

    assert is_component(SimpleComponent)
    component = Component.get_by_cls(SimpleComponent)
    assert component.annotations.get(Route) == [Route('test')]


def test_on_class():

    class SimpleComponent:
        pass

    annotate_class(Route('test'), SimpleComponent)

    assert is_component(SimpleComponent)
    component = Component.get_by_cls(SimpleComponent)
    assert component.annotations.get(Route) == [Route('test')]


def test_on_method():
    class SimpleComponent:

        def method(self):
            pass

        method = annotate_method(Route('test'), method)

    assert SimpleComponent.method.annotations.get(Route) == [Route('test')]


@pytest.mark.parametrize('decorator', (route, route_method))
def test_on_method_by_decorator(decorator):
    class SimpleComponent:

        @decorator('test')
        def method(self):
            pass

    assert SimpleComponent.method.annotations.get(Route) == [Route('test')]


def test_get_one_not_found():
    annotations_ = Annotations()

    with pytest.raises(NotFoundAnnotation) as exception:
        annotations_.get_one(Route)

    assert exception.value.annotation_type == Route
    assert str(exception.value) == f'Not found annotation for {Route}'


def test_get_one_multiple_raises():
    annotations_ = Annotations()
    annotations_.add(Route('first'))
    annotations_.add(Route('second'))

    with pytest.raises(MultipleAnnotationFound) as exception:
        annotations_.get_one(Route)

    assert exception.value.annotation_type == Route
    assert str(exception.value) == f'Found more than one annotation for {Route}: 2'


def test_get_one():
    annotations_ = Annotations()
    annotations_.add(Route('first'))

    annotation = annotations_.get_one(Route)

    assert annotation == Route('first')
