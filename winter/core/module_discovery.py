import importlib
import inspect
import pkgutil
import sys
from typing import List
from typing import Tuple
from typing import Type


class ModuleDiscovery:
    def get_all_classes(self, package: str = None) -> List[Tuple[str, Type]]:
        classes = []
        classes_set = set()
        for module_name, module in dict(sys.modules).items():
            if module_name.endswith('six.moves'):  # pragma: no cover
                continue
            for class_name, class_ in inspect.getmembers(module, inspect.isclass):
                if class_ in classes_set:
                    continue
                if package and not (isinstance(class_.__module__, str) and class_.__module__.startswith(package)):
                    continue
                classes.append((class_name, class_))
                classes_set.add(class_)
        return classes

    def import_recursively(self, package_name: str):
        package = importlib.import_module(package_name)
        for module in pkgutil.iter_modules(package.__path__):
            child_name = package_name + '.' + module.name
            if module.ispkg:
                self.import_recursively(child_name)
            else:
                importlib.import_module(child_name)
