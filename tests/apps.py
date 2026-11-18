from django.apps import AppConfig


class TestAppConfig(AppConfig):
    name = 'tests'

    def ready(self):
        # Importing the URLs creates the application and its URL patterns
        from .urls import urlpatterns   # noqa: F401
