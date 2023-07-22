from django.apps import AppConfig

from winter.web import exception_handlers_registry
from winter.web.exceptions.handlers import DefaultExceptionHandler
# noinspection PyUnresolvedReferences
from .web.interceptors import *  # noqa: F401, F403


class TestAppConfig(AppConfig):
    name = 'tests'

    def ready(self):
        # define this import for force initialization all modules and to register Exceptions
        from .urls import urlpatterns   # noqa: F401
        import winter
        import winter_django
        import winter_openapi

        winter_openapi.setup()
        winter.web.setup()
        winter_django.setup()

        exception_handlers_registry.set_default_handler(DefaultExceptionHandler)  # for 100% test coverage
