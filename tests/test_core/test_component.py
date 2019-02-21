import typing

import dataclasses
import pytest

import winter.core
from winter.core import Component
from winter.core import WinterApplication


def test_is_component():
    winter_app = WinterApplication()

    class SimpleComponent:
        pass

    winter_app.add_component(SimpleComponent)
    assert winter.core.is_component(SimpleComponent)


def test_component_raises():
    with pytest.raises(ValueError):
        winter.core.component(object())


def test_methods():
    class SimpleComponent:

        @winter.core.component_method
        def simple_method(self):
            return self

    component = Component(SimpleComponent)

    assert len(component.methods) == 1, SimpleComponent.simple_method
    method = component.methods[0]

    assert method is SimpleComponent.simple_method
    component = SimpleComponent()
    assert SimpleComponent.simple_method(component) is component


def test_method_state():

    @dataclasses.dataclass(frozen=True)
    class Route:
        path: str

    def route(param: str):
        return winter.core.annotations(Route(param))

    class SimpleComponent:

        @route('/url/')
        def simple_method(self):
            return 123

    assert SimpleComponent.simple_method.annotations.get(Route) == [Route('/url/')]


def test_method_state_many():

    @dataclasses.dataclass(frozen=True)
    class Query:
        value: str

    def query_param(param: str):
        return winter.core.annotations(Query(param))

    class SimpleComponent:

        @query_param('first')
        @query_param('second')
        def simple_method(self):
            return None

    assert SimpleComponent.simple_method.annotations.get(Query) == [Query('second'), Query('first')]
