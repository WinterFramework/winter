import os
from pathlib import Path

import django
import pytest
from injector import CallableProvider
from injector import Injector
from injector import Module
from injector import singleton
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from tests.entities import AuthorizedUser
from winter.core import get_injector
from winter.core import set_injector
from winter_messaging_transactional.injection_modules import BaseModule as MessagingBaseModule
from winter_messaging_transactional.table_metadata import messaging_metadata
from .entities import Guest


def pytest_configure():
    from django.conf import settings
    app_dir = Path(__file__)
    settings.configure(
        ROOT_URLCONF='tests.urls',
        REST_FRAMEWORK={
            'DEFAULT_RENDERER_CLASSES': ('winter_django.renderers.JSONRenderer',),
            'UNAUTHENTICATED_USER': Guest,
        },
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
            'django.contrib.contenttypes',
            # End hack
            'tests',
        ),
    )
    injector = Injector([TestConfiguration, MessagingBaseModule()])
    set_injector(injector)
    django.setup()
    engine = injector.get(Engine)
    messaging_metadata.drop_all(engine)
    messaging_metadata.create_all(engine)


class TestConfiguration(Module):
    def configure(self, binder):
        binder.bind(Engine, to=CallableProvider(make_engine), scope=singleton)


def make_engine():
    url = os.getenv('WINTER_DATABASE_URL')
    return create_engine(url)


@pytest.fixture(scope='session')
def engine() -> Engine:
    injector = get_injector()
    return injector.get(Engine)


@pytest.fixture()
def api_client():
    from rest_framework.test import APIClient

    client = APIClient()
    client.force_authenticate(user=AuthorizedUser())
    return client
