import atexit

from django.apps import AppConfig
from testcontainers.redis import RedisContainer

from tests.web.interceptors import HelloWorldInterceptor
from winter.web import RedisThrottlingConfiguration
from winter.web import exception_handlers_registry
from winter.web import interceptor_registry
from winter.web.exceptions.handlers import DefaultExceptionHandler


class TestAppConfig(AppConfig):
    name = 'tests'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._redis_container: RedisContainer | None = None

    def ready(self):
        # define this import for force initialization all modules and to register Exceptions
        from .urls import urlpatterns   # noqa: F401
        import winter
        import winter_django
        import winter_openapi

        interceptor_registry.add_interceptor(HelloWorldInterceptor())

        winter_openapi.setup()

        winter.web.setup()

        self._redis_container = RedisContainer()
        self._redis_container.start()
        self._redis_container.get_client().flushdb()
        atexit.register(self.cleanup_redis)

        redis_throttling_configuration = RedisThrottlingConfiguration(
            host=self._redis_container.get_container_host_ip(),
            port=self._redis_container.get_exposed_port(self._redis_container.port),
            db=0,
            password=self._redis_container.password
        )
        winter.web.set_redis_throttling_configuration(redis_throttling_configuration)

        winter_django.setup()

        exception_handlers_registry.set_default_handler(DefaultExceptionHandler)  # for 100% test coverage

    def cleanup_redis(self):  # pragma: no cover
        if self._redis_container:
            self._redis_container.stop()
