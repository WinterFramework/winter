from django.apps import AppConfig

from tests.web.interceptors import HelloWorldInterceptor
from winter.web import exception_handlers_registry
from winter.web import interceptor_registry
from winter.web.exceptions.handlers import DefaultExceptionHandler


class TestAppConfig(AppConfig):
    name = 'tests'

    def ready(self):
        # define this import for force initialization all modules and to register Exceptions
        from .urls import urlpatterns   # noqa: F401
        import winter
        import winter_django
        import winter_openapi

        interceptor_registry.add_interceptor(HelloWorldInterceptor())

        winter_openapi.setup()
        winter.web.setup()
        winter_django.setup()

        exception_handlers_registry.set_default_handler(DefaultExceptionHandler)  # for 100% test coverage
