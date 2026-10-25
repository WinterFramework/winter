import subprocess
import sys
from pathlib import Path

import pytest
from injector import Injector

from winter.application import Application
from winter.application import get_injector


class Defined:
    pass


def defined():  # pragma: no cover
    pass


def test_definitions_are_classes_and_functions_defined_in_scanned_modules():
    import tests.application.caller_directory.api
    from tests.application.caller_directory.api import API
    from tests.application.caller_directory.api import function

    # Act
    app = Application(modules=[tests.application.caller_directory.api])

    # Assert
    assert app.definitions == (API, function)


def test_package_is_scanned_with_its_submodules():
    import tests.application.caller_directory.subpackage
    from tests.application.caller_directory.subpackage.deep import Deep

    # Act
    app = Application(modules=[tests.application.caller_directory.subpackage])

    # Assert
    assert app.definitions == (Deep,)


def test_default_modules_are_those_of_caller_directory():
    from tests.application.caller_directory.api import API
    from tests.application.caller_directory.api import function
    from tests.application.caller_directory.subpackage.deep import Deep

    # Act
    from tests.application.caller_directory.app import DefinedBeforeApplication
    from tests.application.caller_directory.app import app

    # Assert
    assert app.definitions == (API, function, DefinedBeforeApplication, Deep)


def test_caller_run_as_main_is_not_executed_twice():
    repository = Path(__file__).parents[2]

    # Act
    result = subprocess.run(
        [sys.executable, '-m', 'tests.application.caller_directory.app'],
        cwd=repository,
        capture_output=True,
        text=True,
        check=True,
    )

    # Assert
    assert result.stdout.splitlines() == ['executing __main__', 'API function DefinedBeforeApplication Deep']


def test_unimportable_module_fails_construction():
    import tests.application.unimportable

    # Act
    with pytest.raises(RuntimeError, match='Unimportable') as exception_info:
        Application(modules=[tests.application.unimportable])

    # Assert
    assert exception_info.value.__notes__ == [
        'Application imports every module of tests.application.unimportable, so each of them must be importable',
    ]


def test_add():
    app = Application(modules=[])

    # Act
    app.add(Defined)
    app.add(defined)
    app.add(Defined)

    # Assert
    assert app.definitions == (Defined, defined)


def test_new_injector_is_not_installed_globally():
    # Act
    app = Application(modules=[])

    # Assert
    assert isinstance(app.injector, Injector)
    assert get_injector() is not app.injector


def test_given_injector_is_shared():
    injector = Injector()

    # Act
    app_1 = Application(modules=[], injector=injector)
    app_2 = Application(modules=[], injector=injector)

    # Assert
    assert app_1.injector is injector
    assert app_2.injector is injector
