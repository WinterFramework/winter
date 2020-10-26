from django.apps import AppConfig


class TestAppConfig(AppConfig):
    name = 'test'

    def ready(self):
        # define this import for force initialization all modules and to register Exceptions
        from .urls import urlpatterns   # noqa: F401
        import winter
        import winter_django
        import winter_openapi

        winter_openapi.setup()
        winter.web.setup()
        winter_django.setup()
