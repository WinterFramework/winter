from django.apps import AppConfig


class TestAppConfig(AppConfig):
    name = 'test'

    def ready(self):
        from .urls import urlpatterns
        import winter
        import winter_django
        import winter_openapi

        winter_openapi.setup()
        winter.web.setup()
        winter_django.setup()
