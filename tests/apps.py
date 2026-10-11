from http import HTTPStatus

from django.apps import AppConfig

from tests.web.interceptors import HelloWorldInterceptor
from winter.ddd import NotFoundException
from winter.web import InMemoryThrottlingStorage
from winter.web import exception_handlers_registry
from winter.web import interceptor_registry
from winter.web.exceptions.handlers import DefaultExceptionHandler


class TestAppConfig(AppConfig):
    name = 'tests'

    def ready(self):
        # define this import for force initialization all modules and to register Exceptions
        from .urls import urlpatterns   # noqa: F401
        import winter
        import winter.django
        import winter.openapi

        interceptor_registry.add_interceptor(HelloWorldInterceptor())

        winter.openapi.setup()

        # Mapping a domain exception to an HTTP status is application wiring, not framework behaviour
        winter.web.problem(status=HTTPStatus.NOT_FOUND)(NotFoundException)
        winter.web.setup()

        # The Redis storage is covered in tests/redis; the sample application throttles in memory.
        winter.web.set_throttling_storage(InMemoryThrottlingStorage())

        winter.django.setup()

        exception_handlers_registry.set_default_handler(DefaultExceptionHandler)  # for 100% test coverage
