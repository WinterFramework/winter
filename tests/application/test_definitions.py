import pytest

from winter.application import find_definitions


def test_definitions_are_classes_and_functions_defined_in_modules():
    import tests.application.scanned.api
    from tests.application.scanned.api import API
    from tests.application.scanned.api import function

    # Act
    definitions = find_definitions([tests.application.scanned.api])

    # Assert
    assert definitions == (API, function)


def test_package_is_scanned_with_its_submodules():
    import tests.application.scanned.subpackage
    from tests.application.scanned.subpackage.deep import Deep

    # Act
    definitions = find_definitions([tests.application.scanned.subpackage])

    # Assert
    assert definitions == (Deep,)


def test_directory_without_init_is_not_scanned():
    import tests.application.scanned
    from tests.application.scanned.api import API
    from tests.application.scanned.api import function
    from tests.application.scanned.subpackage.deep import Deep

    # Act
    definitions = find_definitions([tests.application.scanned])

    # Assert
    assert definitions == (API, function, Deep)


def test_definition_of_module_given_twice_is_found_once():
    import tests.application.scanned
    import tests.application.scanned.subpackage
    from tests.application.scanned.api import API
    from tests.application.scanned.api import function
    from tests.application.scanned.subpackage.deep import Deep

    # Act
    definitions = find_definitions([tests.application.scanned, tests.application.scanned.subpackage])

    # Assert
    assert definitions == (API, function, Deep)


def test_unimportable_module_fails():
    import tests.application.unimportable

    # Act
    with pytest.raises(RuntimeError, match='Unimportable') as exception_info:
        find_definitions([tests.application.unimportable])

    # Assert
    assert exception_info.value.__notes__ == [
        'Finding the definitions imports every module of tests.application.unimportable, '
        'so each of them must be importable',
    ]
