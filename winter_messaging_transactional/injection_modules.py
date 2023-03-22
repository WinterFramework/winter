from injector import CallableProvider
from injector import ClassProvider
from injector import Module
from injector import singleton
from pika import BlockingConnection

from winter.messaging import EventHandlerRegistry
from winter.messaging.event_dispacher import EventDispatcher
from winter_messaging_transactional.consumer import ConsumerWorker
from winter_messaging_transactional.consumer import MiddlewareRegistry
from winter_messaging_transactional.consumer.inbox.inbox_leanup_processor import InboxCleanupProcessor
from winter_messaging_transactional.consumer.inbox.inbox_message_dao import InboxMessageDAO
from winter_messaging_transactional.producer.outbox import OutboxMessageDAO
from winter_messaging_transactional.producer.outbox.outbox_cleanup_processor import OutboxCleanupProcessor
from winter_messaging_transactional.producer.publish_processor import PublishProcessor
from winter_messaging_transactional.rabbitmq import TopologyConfigurator
from winter_messaging_transactional.rabbitmq import create_connection


class BaseModule(Module):
    def configure(self, binder):
        binder.bind(EventHandlerRegistry, to=ClassProvider(EventHandlerRegistry), scope=singleton)
        binder.bind(EventDispatcher, to=ClassProvider(EventDispatcher))
        binder.bind(TopologyConfigurator, to=ClassProvider(TopologyConfigurator), scope=singleton)
        binder.bind(BlockingConnection, to=CallableProvider(create_connection), scope=singleton)


class ConsumerModule(Module):
    def configure(self, binder):
        binder.bind(ConsumerWorker, to=ClassProvider(ConsumerWorker))
        binder.bind(MiddlewareRegistry, to=ClassProvider(MiddlewareRegistry), scope=singleton)
        binder.bind(InboxCleanupProcessor, to=ClassProvider(InboxCleanupProcessor))
        binder.bind(InboxMessageDAO, to=ClassProvider(InboxMessageDAO))


class ProducerModule(Module):
    def configure(self, binder):
        binder.bind(OutboxMessageDAO, to=ClassProvider(OutboxMessageDAO))
        binder.bind(PublishProcessor, to=ClassProvider(PublishProcessor))
        binder.bind(OutboxCleanupProcessor, to=ClassProvider(OutboxCleanupProcessor))
