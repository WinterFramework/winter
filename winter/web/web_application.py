import inspect
from collections.abc import Sequence
from types import ModuleType
from typing import Literal

from injector import Injector

from winter.application import Definition
from winter.application import find_definitions
from .interceptor import Interceptor


class WebApplication:
    """
    The code of a web application, the injector it runs with and the interceptors of its requests, in one object that
    adapters build from. The classes and functions defined in the modules are its definitions: the API classes, the
    exception handlers and the @problem exceptions among them belong to it.
    """

    def __init__(
        self,
        modules: Sequence[ModuleType],
        injector: Injector | Literal['new'] = 'new',
        interceptors: Sequence[type[Interceptor]] = (),
    ):
        """The interceptors run in the given order and are created by the injector of each request."""
        for interceptor in interceptors:
            if not inspect.isclass(interceptor):
                raise TypeError(f'Interceptors are classes created by the injector: {type(interceptor).__qualname__}()')
            if not issubclass(interceptor, Interceptor):
                raise TypeError(f'{interceptor.__qualname__} is not an Interceptor')
        self.injector = Injector() if injector == 'new' else injector
        self.interceptors = tuple(interceptors)
        self._definitions = dict.fromkeys(find_definitions(modules))

    @property
    def definitions(self) -> tuple[Definition, ...]:
        """Classes and functions of the application, in the order they were scanned or added."""
        return tuple(self._definitions)

    def add(self, definition: Definition) -> None:
        """
        Adds a class or a function that is not defined in the modules, such as a generated one. Adapters take the
        definitions when they build from the application, so one added afterwards is not served.
        """
        self._definitions.setdefault(definition, None)
