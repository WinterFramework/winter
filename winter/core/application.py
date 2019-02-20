import types
import typing
import weakref

from .component import Component


class WinterApplication:

    def __init__(self):
        self._components = weakref.WeakKeyDictionary()

    @property
    def components(self) -> types.MappingProxyType:
        return types.MappingProxyType(self._components)

    def add_component(self, cls: typing.Type) -> typing.Type:
        Component.register(cls)
        self._components[cls] = Component(cls)
        return cls

    def autodiscover(self) -> None:
        for component_cls in Component.get_all_component_classes():
            if component_cls not in self._components:
                self.add_component(component_cls)
