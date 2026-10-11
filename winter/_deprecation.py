"""
Aliases for import paths that moved in 33.0. Removed in 34.0.

An old module name resolves to the very same module object as the new one, so
`winter.core.json is winter.json`. Importing through an old name emits a DeprecationWarning.
"""
import importlib
import importlib.abc
import importlib.util
import sys
import warnings
from typing import Dict
from typing import Optional


class _AliasFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self):
        self._exact: Dict[str, str] = {}
        self._prefixes: Dict[str, str] = {}

    def add(self, exact: Dict[str, str] = None, prefixes: Dict[str, str] = None):
        self._exact.update(exact or {})
        self._prefixes.update(prefixes or {})

    def translate(self, fullname: str) -> Optional[str]:
        if fullname in self._exact:
            return self._exact[fullname]
        for old_prefix in sorted(self._prefixes, key=len, reverse=True):
            if fullname == old_prefix or fullname.startswith(old_prefix + '.'):
                return self._prefixes[old_prefix] + fullname[len(old_prefix):]
        return None

    def find_spec(self, fullname, path=None, target=None):
        if self.translate(fullname) is None:
            return None
        return importlib.util.spec_from_loader(fullname, self)

    def create_module(self, spec):
        new_name = self.translate(spec.name)
        warnings.warn(f'{spec.name} is deprecated, use {new_name}', DeprecationWarning, stacklevel=2)
        return importlib.import_module(new_name)

    def exec_module(self, module):
        pass


_finder = _AliasFinder()


def alias_modules(exact: Dict[str, str] = None, prefixes: Dict[str, str] = None):
    """
    Register old -> new module names. `exact` maps single modules, `prefixes` map a whole subtree:
    {'winter.core.json': 'winter.json'} makes winter.json.decoder resolve to winter.json.decoder.
    """
    if _finder not in sys.meta_path:
        sys.meta_path.insert(0, _finder)
    _finder.add(exact, prefixes)


def deprecated_package(old_name: str, new_name: str):
    warnings.warn(f'{old_name} is deprecated, use {new_name}', DeprecationWarning, stacklevel=3)
