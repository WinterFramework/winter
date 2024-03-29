import inspect
from typing import Dict
from typing import Mapping
from typing import Optional
from typing import TYPE_CHECKING
from typing import Type

from .annotations import Annotations

if TYPE_CHECKING:  # pragma: no cover
    from .component_method import ComponentMethod


class Component:
    _components = {}

    def __init__(self, component_cls: Type):
        self.component_cls = component_cls
        self.annotations = Annotations()
        self._methods: Dict[str, 'ComponentMethod'] = {}

    def __repr__(self):
        return f'Component(component_cls={self.component_cls.__name__})'

    @property
    def methods(self):
        return self._methods.values()

    def get_method(self, name: str) -> Optional['ComponentMethod']:
        return self._methods.get(name)

    def add_method(self, method: 'ComponentMethod'):
        method_name = method.name
        assert method_name not in self._methods, 'Component cannot have two methods with same name'
        self._methods[method_name] = method

    @classmethod
    def register(cls, cls_: Type) -> 'Component':
        if not inspect.isclass(cls_):
            cls._raise_invalid_class(cls_)
        instance = cls._components.get(cls_)
        if instance is None:
            instance = cls._components[cls_] = cls(cls_)
        return instance

    @classmethod
    def get_all(cls) -> Mapping:
        return cls._components

    @classmethod
    def get_by_cls(cls, component_cls) -> 'Component':
        if not inspect.isclass(component_cls):
            cls._raise_invalid_class(component_cls)
        component_ = cls._components.get(component_cls)
        if component_ is None:
            component_ = cls.register(component_cls)
        return component_

    @classmethod
    def _raise_invalid_class(cls, cls_):
        raise ValueError(f'Need class. Got: {cls_}')


def is_component(cls: Type) -> bool:
    return cls in Component.get_all()


def component(cls: Type) -> Type:
    if not inspect.isclass(cls):
        raise ValueError(f'Need class. Given: {cls}')
    Component.register(cls)
    return cls
