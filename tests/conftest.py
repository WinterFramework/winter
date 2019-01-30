import django
import pytest


def pytest_configure():
    from django.conf import settings

    settings.configure()
    django.setup()


@pytest.fixture
def clear_resolvers():
    from winter.argument_resolver import _resolvers
    _resolvers.clear()
