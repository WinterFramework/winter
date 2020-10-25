from pathlib import Path

import django

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
            'tests',
        ),
    )
    django.setup()
