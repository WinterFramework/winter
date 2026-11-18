import importlib
import inspect
import types
from collections.abc import Sequence

from .module_discovery import import_recursively

Definition = type | types.FunctionType


def find_definitions(modules: Sequence[types.ModuleType]) -> tuple[Definition, ...]:
    """
    The classes and functions defined in the modules, in the order they are scanned. Each module is imported together
    with its submodules. A directory without `__init__.py` is not a package and is not scanned.
    """
    definitions: dict[Definition, None] = {}
    for module in modules:
        for scanned_module in _import_recursively(module.__name__):
            for definition in _defined_in(scanned_module):
                definitions.setdefault(definition, None)
    return tuple(definitions)


def _import_recursively(module_name: str) -> list[types.ModuleType]:
    try:
        module = importlib.import_module(module_name)
        return [module, *import_recursively(module_name)] if hasattr(module, '__path__') else [module]
    except Exception as error:
        error.add_note(
            f'Finding the definitions imports every module of {module_name}, so each of them must be importable',
        )
        raise


def _defined_in(module: types.ModuleType):
    for value in vars(module).values():
        if (inspect.isclass(value) or inspect.isfunction(value)) and value.__module__ == module.__name__:
            yield value
