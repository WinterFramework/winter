import importlib
import inspect
import os
import pkgutil
import sys
import types
from collections.abc import Sequence
from typing import Any
from typing import Literal

from injector import Injector

from .module_discovery import import_recursively

Definition = type | types.FunctionType


class Application:
    """
    The code of an application and the injector it runs with, in one object that adapters build from.

    The modules are scanned on construction: each one is imported together with its submodules, and the
    classes and functions defined in them become the application's definitions. A directory without
    `__init__.py` is not a package and is not scanned. By default, the modules are those of the directory
    of the module that creates the Application.
    """

    def __init__(
        self,
        modules: Sequence[types.ModuleType] | Literal['caller_directory'] = 'caller_directory',
        injector: Injector | Literal['new'] = 'new',
    ):
        self.injector = Injector() if injector == 'new' else injector
        if modules == 'caller_directory':
            module_names = _caller_directory(sys._getframe(1).f_globals)
        else:
            module_names = [module.__name__ for module in modules]
        self._definitions: dict[Definition, None] = {}
        for module_name in module_names:
            for module in _import_recursively(module_name):
                for definition in _defined_in(module):
                    self.add(definition)

    @property
    def definitions(self) -> tuple[Definition, ...]:
        """Classes and functions of the application, in the order they were scanned or added."""
        return tuple(self._definitions)

    def add(self, definition: Definition) -> None:
        """Adds a class or a function that is not defined in the scanned modules, such as a generated one."""
        self._definitions.setdefault(definition, None)


def _caller_directory(caller_globals: dict[str, Any]) -> list[str]:
    path = caller_globals['__file__']
    package = caller_globals['__package__']
    prefix = f'{package}.' if package else ''
    caller_name = prefix + inspect.getmodulename(path)
    module_names = [prefix + module.name for module in pkgutil.iter_modules([os.path.dirname(path)])]
    # Run with `python -m`, the caller is __main__: importing it by its own name would execute it a second time
    return [caller_globals['__name__'] if name == caller_name else name for name in module_names]


def _import_recursively(module_name: str) -> list[types.ModuleType]:
    try:
        module = importlib.import_module(module_name)
        return [module, *import_recursively(module_name)] if hasattr(module, '__path__') else [module]
    except Exception as error:
        error.add_note(f'Application imports every module of {module_name}, so each of them must be importable')
        raise


def _defined_in(module: types.ModuleType):
    for value in vars(module).values():
        if (inspect.isclass(value) or inspect.isfunction(value)) and value.__module__ == module.__name__:
            yield value
