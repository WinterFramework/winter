from pathlib import Path

import django
import pytest
from injector import CallableProvider
from injector import Injector
from injector import Module
from injector import singleton
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from winter.core import set_injector


def pytest_configure():
    from django.conf import settings
    app_dir = Path(__file__)
    settings.configure(
        ROOT_URLCONF='tests.urls',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [app_dir.parent.name + '/templates'],
                'APP_DIRS': True,
                'OPTIONS': {
                    'debug': True,  # We want template errors to raise
                },
            },
        ],
        INSTALLED_APPS=(
            # Hack for making module discovery working
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            # End hack
            'tests',
        ),
        MIDDLEWARE=[
            'tests.middleware.AuthenticationMiddleware',
        ],
        SECRET_KEY='Test secret key',
    )
    injector = Injector([Configuration])
    set_injector(injector)
    django.setup()


class Configuration(Module):
    def configure(self, binder):
        binder.bind(Engine, to=CallableProvider(make_engine), scope=singleton)


def make_engine():
    return create_engine('sqlite://')


@pytest.fixture(scope='session')
def wsgi():
    from django.core.wsgi import get_wsgi_application
    return get_wsgi_application()


@pytest.fixture()
def api_client(wsgi):
    import httpx
    return httpx.Client(app=wsgi, base_url='http://testserver')
