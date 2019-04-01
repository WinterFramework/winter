import inspect

from winter.core import ComponentMethod
from winter.core import ComponentMethodArgument
from winter.core import WinterApplication
from winter.core import component_method


def test_all_attributes():
    winter_app = WinterApplication()
    argument_type = int
    argument_name = 'number'
    method_name = 'method'

    class SimpleComponent:

        @component_method
        def method(self, number: argument_type):
            return self, number

    winter_app.add_component(SimpleComponent)
    simple_component = SimpleComponent()

    cls_method = SimpleComponent.method

    assert cls_method.component == winter_app.components[SimpleComponent]
    assert cls_method.name == method_name
    assert inspect.ismethod(simple_component.method)
    assert cls_method.func == simple_component.method.__func__
    assert cls_method(simple_component, 123) == (simple_component, 123)
    assert simple_component.method(123) == (simple_component, 123)
    number_argument = ComponentMethodArgument(cls_method, argument_name, argument_type)
    assert cls_method.arguments == (number_argument,)
    assert number_argument == cls_method.get_argument(argument_name)


def test_component_method():
    def test():
        return None

    method = ComponentMethod(test)
    assert method is component_method(method)
