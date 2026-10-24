from django.apps import AppConfig

from tests.web.interceptors import HelloWorldInterceptor
import winter.web
from winter.web import InMemoryThrottlingStorage
from winter.web import interceptor_registry


class TestAppConfig(AppConfig):
    name = 'tests'

    def ready(self):
        # Importing the URLs creates the application and its URL patterns
        from .urls import urlpatterns   # noqa: F401

        interceptor_registry.add_interceptor(HelloWorldInterceptor())

        # The Redis storage is covered in tests/redis; the sample application throttles in memory.
        winter.web.set_throttling_storage(InMemoryThrottlingStorage())
