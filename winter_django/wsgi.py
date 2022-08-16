def create_wsgi(scan_package: str):
    from django.core.wsgi import get_wsgi_application
    from django.conf import settings

    class URLConf:
        def __init__(self):
            self.urlpatterns = []
    urlconf = URLConf()

    settings.configure(
        ROOT_URLCONF=urlconf,
        REST_FRAMEWORK={
            'DEFAULT_RENDERER_CLASSES': ('winter_django.renderers.JSONRenderer',),
            'UNAUTHENTICATED_USER': object,
        },
        INSTALLED_APPS=(
            # Hack for making module discovery working
            'django.contrib.admin',
            'django.contrib.contenttypes',
            # End hack
        ),
    )

    import django
    import winter.core
    import winter_django
    import winter_openapi
    from injector import Injector

    winter.core.set_injector(Injector())
    winter.web.setup()
    winter_django.setup()
    winter_openapi.setup(allow_missing_raises_annotation=True)
    django.setup()

    import winter_django.autodiscovery
    urlconf.urlpatterns = winter_django.autodiscovery.create_django_urls_for_package(scan_package)

    return get_wsgi_application()

