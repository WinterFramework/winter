import django


def pytest_configure():
    from django.conf import settings

    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'rest_framework',
            'tests',
        ],
        ROOT_URLCONF='tests.urls'
    )
    django.setup()
