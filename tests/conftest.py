import django
import pytest


def pytest_configure():
    from django.conf import settings
    settings.configure(
        ROOT_URLCONF='tests.urls',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
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
    django.setup()


@pytest.fixture(scope='session')
def wsgi():
    from django.core.wsgi import get_wsgi_application
    return get_wsgi_application()


@pytest.fixture()
def api_client(wsgi):
    import httpx
    return httpx.Client(app=wsgi, base_url='http://testserver')
