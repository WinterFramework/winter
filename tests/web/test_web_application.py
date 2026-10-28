import pytest
from injector import Injector

import winter.web


class _Defined:
    pass


def _defined():  # pragma: no cover
    pass


def test_definitions_are_those_of_modules():
    import tests.application.scanned.api
    from tests.application.scanned.api import API
    from tests.application.scanned.api import function

    # Act
    app = winter.web.WebApplication(modules=[tests.application.scanned.api])

    # Assert
    assert app.definitions == (API, function)


def test_add():
    app = winter.web.WebApplication(modules=[])

    # Act
    app.add(_Defined)
    app.add(_defined)
    app.add(_Defined)

    # Assert
    assert app.definitions == (_Defined, _defined)


def test_new_injector_is_own_injector_of_application():
    # Act
    app_1 = winter.web.WebApplication(modules=[])
    app_2 = winter.web.WebApplication(modules=[])

    # Assert
    assert isinstance(app_1.injector, Injector)
    assert app_1.injector is not app_2.injector


def test_given_injector_is_shared():
    injector = Injector()

    # Act
    app_1 = winter.web.WebApplication(modules=[], injector=injector)
    app_2 = winter.web.WebApplication(modules=[], injector=injector)

    # Assert
    assert app_1.injector is injector
    assert app_2.injector is injector


class _Interceptor(winter.web.Interceptor):
    def pre_handle(self):  # pragma: no cover
        pass


@pytest.mark.parametrize('interceptor, expected_message', [
    (_Interceptor(), 'Interceptors are classes created by the injector: _Interceptor()'),
    (_Defined, '_Defined is not an Interceptor'),
])
def test_interceptor_must_be_interceptor_class(interceptor, expected_message):
    # Act
    with pytest.raises(TypeError) as exception_info:
        winter.web.WebApplication(modules=[], interceptors=[interceptor])

    # Assert
    assert str(exception_info.value) == expected_message
