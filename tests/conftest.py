import django

from .entities import Guest


def pytest_configure():
    from django.conf import settings
    settings.configure(
        ROOT_URLCONF='tests.urls',
        REST_FRAMEWORK={
            'DEFAULT_RENDERER_CLASSES': ('winter.json_renderer.JSONRenderer',),
            'UNAUTHENTICATED_USER': Guest,
        },
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
            'tests',
        ),
    )
    django.setup()
