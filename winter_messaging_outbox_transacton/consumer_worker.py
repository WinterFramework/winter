from injector import CallableProvider
from injector import ClassProvider
from injector import Injector
from injector import Module
from injector import inject
from injector import singleton
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError
from retry import retry
from sqlalchemy.engine import Engine

from tests.conftest import make_engine
from winter.messaging import EventHandlerRegistry
from winter_messaging_outbox_transacton.inbox.inbox_message import inbox_metadata
from winter_messaging_outbox_transacton.message_listener import MessageListener
from winter_messaging_outbox_transacton.rabbitmq import TopologyConfigurator
from winter_messaging_outbox_transacton.rabbitmq import connect_to_rabbit


class ConsumerWorker:
    @inject
    def __init__(
        self,
        event_handler_registry: EventHandlerRegistry,
        configurator: TopologyConfigurator,
        message_listener: MessageListener,
        channel: BlockingChannel,
    ) -> None:
        self._event_handler_registry = event_handler_registry
        self._configurator = configurator
        self._message_listener = message_listener
        self._channel = channel

    def start(self, consumer_id, package_name: str):
        self._message_listener.consumer_id = consumer_id
        self._configurator.autodiscover(package_name)
        configuration = self._configurator.configure_topics()
        self._configurator.configure_listener(
            consumer_id,
            configuration,
            self._message_listener.on_message_callback,
        )

        self._start_with_retry(consumer_id)

    @retry(AMQPConnectionError, delay=5, jitter=(1, 3))
    def _start_with_retry(self, consumer_id):
        # TODO add reconnect method
        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            print(f"Consumer worker {consumer_id} stopping by KeyboardInterrupt")
            self._channel.stop_consuming()
        self._channel.connection.close()


class Configuration(Module):
    def configure(self, binder):
        binder.bind(Engine, to=CallableProvider(make_engine), scope=singleton)
        binder.bind(BlockingChannel, to=CallableProvider(connect_to_rabbit), scope=singleton)
        binder.bind(EventHandlerRegistry, to=ClassProvider(EventHandlerRegistry), scope=singleton)


if __name__ == '__main__':
    consumer_id = 'winter_sample'
    package_name = 'samples.event_driven_communication'

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

    injector = Injector([Configuration])
    winter.core.set_injector(injector)
    winter_django.setup()
    django.setup()

    injector = winter.core.get_injector()
    engine = injector.get(Engine)
    inbox_metadata.create_all(bind=engine)
    worker = injector.get(ConsumerWorker)
    print(f'Starting message consumer id: {consumer_id}; in package: {package_name}')
    worker.start(consumer_id=consumer_id, package_name=package_name)
