import django


def pytest_configure():
    from django.conf import settings

    settings.configure(
        ROOT_URLCONF='tests.urls'
    )
    django.setup()
