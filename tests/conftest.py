import django


def pytest_configure():
    from django.conf import settings
    settings.configure(
        ROOT_URLCONF='tests.urls',
        REST_FRAMEWORK={
            'DEFAULT_RENDERER_CLASSES': ('winter.json_renderer.JSONRenderer',),
        },
    )
    django.setup()
