"""Old import paths keep working until 34.0 and resolve to the same module objects as the new ones."""
import importlib
import sys

import pytest


def _reimport(name: str):
    sys.modules.pop(name, None)
    return importlib.import_module(name)


def test_winter_core_is_an_alias_of_components_and_application():
    with pytest.warns(DeprecationWarning, match='winter.core is deprecated'):
        core = _reimport('winter.core')

    import winter.application
    import winter.components

    assert core.Component is winter.components.Component
    assert core.annotate is winter.components.annotate
    assert core.get_injector is winter.application.get_injector
    assert core.WinterApplication is winter.application.WinterApplication


@pytest.mark.parametrize('old_name, new_name', [
    ('winter.core.component', 'winter.components.component'),
    ('winter.core.json', 'winter.json'),
    ('winter.core.json.decoder', 'winter.json.decoder'),
    ('winter.core.module_discovery', 'winter.application.module_discovery'),
    ('winter.core.utils.typing', 'winter.components.typing'),
    ('winter.data.pagination', 'winter.pagination'),
    ('winter.data.pagination.sort', 'winter.pagination.sort'),
    ('winter.data.repository', 'winter.ddd.repository'),
    ('winter.data.exceptions', 'winter.ddd.exceptions'),
    ('winter_ddd.aggregate_root', 'winter.ddd.aggregate_root'),
    ('winter_openapi.generator', 'winter.openapi.generator'),
    ('winter_openapi.inspectors.page_inspector', 'winter.openapi.inspectors.page_inspector'),
    ('winter_django.view', 'winter.django.view'),
    ('winter_sqlalchemy.repository', 'winter.sqlalchemy.repository'),
])
def test_old_module_is_the_new_module(old_name, new_name):
    with pytest.warns(DeprecationWarning, match=f'{old_name} is deprecated, use {new_name}'):
        old_module = _reimport(old_name)

    assert old_module is importlib.import_module(new_name)


def test_winter_core_utils_exports_the_former_names():
    from winter.components.nested_types import TypeWrapper
    from winter.web.pagination.positive_integer import PositiveInteger

    with pytest.warns(DeprecationWarning, match='winter.core.utils is deprecated'):
        utils = _reimport('winter.core.utils')

    assert utils.TypeWrapper is TypeWrapper
    assert utils.PositiveInteger is PositiveInteger


def test_winter_data_exports_crud_repository():
    import winter.ddd

    with pytest.warns(DeprecationWarning, match='winter.data is deprecated'):
        data = _reimport('winter.data')

    assert data.CRUDRepository is winter.ddd.CRUDRepository


@pytest.mark.parametrize('old_name, new_name', [
    ('winter_ddd', 'winter.ddd'),
    ('winter_openapi', 'winter.openapi'),
    ('winter_django', 'winter.django'),
    ('winter_sqlalchemy', 'winter.sqlalchemy'),
])
def test_old_top_level_package_exports_the_new_names(old_name, new_name):
    with pytest.warns(DeprecationWarning, match=f'{old_name} is deprecated, use {new_name}'):
        old_package = _reimport(old_name)
    new_package = importlib.import_module(new_name)

    public_names = [name for name in dir(new_package) if not name.startswith('_')]
    assert public_names
    assert all(getattr(old_package, name) is getattr(new_package, name) for name in public_names)


def test_unknown_old_module_is_not_invented():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module('winter.core.no_such_module')
