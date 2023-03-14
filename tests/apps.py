from django.apps import AppConfig
from injector import ClassProvider
from injector import InstanceProvider

# noinspection PyUnresolvedReferences
from .web.interceptors import *  # noqa: F401, F403


class TestAppConfig(AppConfig):
    name = 'tests'

    def ready(self):
        from winter.core import get_injector
        from winter.messaging import MessagingConfig
        from tests.winter_messaging.app_sample import topology_config
        from winter.messaging import EventPublisher
        from winter_messaging_outbox_transacton.outbox import OutboxEventPublisher

        # define this import for force initialization all modules and to register Exceptions
        from .urls import urlpatterns   # noqa: F401
        import winter
        import winter_django
        import winter_openapi
        import winter_messaging_outbox_transacton

        winter_openapi.setup()
        winter.web.setup()
        winter_django.setup()
        winter_messaging_outbox_transacton.setup()

        injector = get_injector()
        injector.binder.bind(EventPublisher, to=ClassProvider(OutboxEventPublisher))
        injector.binder.bind(MessagingConfig, to=InstanceProvider(topology_config))
