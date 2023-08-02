from injector import ClassProvider
from injector import InstanceProvider
from injector import Module
from injector import singleton

from winter.messaging import EventHandlerRegistry
from winter.messaging.event_dispacher import EventDispatcher
from winter_messaging_transactional.consumer import ConsumerWorker
from winter_messaging_transactional.consumer import MiddlewareCollection
from winter_messaging_transactional.consumer import MiddlewareRegistry
from winter_messaging_transactional.consumer.inbox_cleanup_processor import InboxCleanupProcessor
from winter_messaging_transactional.consumer.inbox.inbox_message_dao import InboxMessageDAO
from winter_messaging_transactional.producer.outbox import OutboxMessageDAO
from winter_messaging_transactional.producer.outbox_cleanup_processor import OutboxCleanupProcessor
from winter_messaging_transactional.producer.publish_processor import PublishProcessor
from winter_messaging_transactional.rabbitmq import TopologyConfigurator


class TransactionalMessagingModule(Module):
    def configure(self, binder):
        binder.bind(EventHandlerRegistry, to=ClassProvider(EventHandlerRegistry), scope=singleton)
        binder.bind(EventDispatcher, to=ClassProvider(EventDispatcher))
        binder.bind(TopologyConfigurator, to=ClassProvider(TopologyConfigurator), scope=singleton)
        binder.bind(ConsumerWorker, to=ClassProvider(ConsumerWorker))
        binder.bind(MiddlewareRegistry, to=ClassProvider(MiddlewareRegistry), scope=singleton)
        binder.bind(InboxCleanupProcessor, to=ClassProvider(InboxCleanupProcessor))
        binder.bind(InboxMessageDAO, to=ClassProvider(InboxMessageDAO))
        binder.bind(MiddlewareCollection, to=InstanceProvider([]))
        binder.bind(OutboxMessageDAO, to=ClassProvider(OutboxMessageDAO))
        binder.bind(PublishProcessor, to=ClassProvider(PublishProcessor))
        binder.bind(OutboxCleanupProcessor, to=ClassProvider(OutboxCleanupProcessor))

