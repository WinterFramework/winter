from unittest.mock import Mock

from injector import Injector
from injector import Module

from winter.injection import setup_injector


def test_setup_injector_without_configuration():
    injector = setup_injector()
    assert isinstance(injector, Injector)


def test_setup_injector_with_one_configuration_module():
    module = ModuleMock()

    injector = setup_injector(configuration=module)
    assert isinstance(injector, Injector)
    module.assert_configured()


def test_setup_injector_with_multiple_configuration_modules():
    module_1 = ModuleMock()
    module_2 = ModuleMock()

    injector = setup_injector(configuration=[module_1, module_2])
    assert isinstance(injector, Injector)
    module_1.assert_configured()
    module_2.assert_configured()


class ModuleMock(Module):
    def __init__(self):
        super().__init__()
        self._configure_mock = Mock()

    def configure(self, binder):
        self._configure_mock()

    def assert_configured(self):
        self._configure_mock.assert_called_once()
