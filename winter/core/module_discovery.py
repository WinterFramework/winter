import importlib
import inspect
import pkgutil
import sys
from types import ModuleType
from typing import List, Generator, Dict, Union
from typing import Tuple
from typing import Type


def get_all_classes(package: str) -> Generator[Tuple[str, Type], None, None]:
    classes_set = set()
    for module in import_recursively(package):
        try:
            for class_name, class_ in inspect.getmembers(module, inspect.isclass):
                if class_ in classes_set:
                    continue
                if not class_.__module__.startswith(package):
                    continue
                yield class_name, class_
                classes_set.add(class_)
        except ImportError:
            pass


def get_all_subclasses(supertype: Type) -> Generator[Tuple[str, Type], None, None]:
    for module in dict(sys.modules).values():
        try:
            for class_name, class_ in inspect.getmembers(module, inspect.isclass):
                try:
                    # Workaround to not fail in the issubclass check
                    from _weakref import ReferenceType

                    ReferenceType(class_)
                except TypeError:
                    continue
                if class_ is not supertype and issubclass(class_, supertype):
                    yield class_name, class_
        except ImportError:  # pragma: no cover
            pass


def import_recursively(package: str) -> Generator[ModuleType, None, None]:
    package = importlib.import_module(package)
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        yield importlib.import_module(name)
