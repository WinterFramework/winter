import logging
from collections import defaultdict
from typing import Dict

from injector import inject

from winter.core import Component
from winter.messaging import EventHandlerRegistry
from winter.messaging import get_event_topic
from winter.messaging import TopicAnnotation
from winter.messaging import MessagingConfig
from winter_messaging_transactional.rabbitmq.rabbitmq_client import RabbitMQClient
from winter_messaging_transactional.naming_convention import get_consumer_queue
from winter_messaging_transactional.naming_convention import get_exchange_name
from winter_messaging_transactional.naming_convention import get_routing_key


log = logging.getLogger(__name__)


class InvalidTopologyException(Exception):
    pass


class TopologyConfigurator:
    @inject
    def __init__(
        self,
        rabbit_client: RabbitMQClient,
        handler_registry: EventHandlerRegistry,
        config: MessagingConfig
    ) -> None:
        self._rabbit_client = rabbit_client
        self._handler_registry = handler_registry
        self._config = config
        self._topic_to_exchange_map: Dict[str, str] = {}
        self._consumer_id_to_queue = {}
        self._consumer_to_events_map = defaultdict(set)
        self._configure()

    def _configure(self):
        for consumer_id, packages in self._config.consumers.items():
            for package_name in packages:
                self._handler_registry.autodiscover(consumer_id, package_name)

        all_handlers = self._handler_registry.get_all_handlers()
        discovered_topics = set()
        for handler_info in all_handlers:
            event_type = handler_info.arguments[0].type_
            component = Component.get_by_cls(event_type)
            topic_annotation = component.annotations.get_one_or_none(TopicAnnotation)
            if not topic_annotation:
                msg = f'Event "{event_type}" must be annotated with @topic for handler: "{handler_info.name}"'
                raise InvalidTopologyException(msg)

            topic_info = get_event_topic(event_type)
            topic_name = topic_info.name
            discovered_topics.add(topic_name)
            event_routing_key = get_routing_key(topic_name, topic_info.event_name)
            exchange_name = get_exchange_name(topic_name)
            self._topic_to_exchange_map[topic_name] = exchange_name
            key = (exchange_name, event_routing_key)
            # TODO fix monkey patching consumer_id in self._handler_registry.autodiscover
            consumer_id = handler_info.consumer_id
            self._consumer_to_events_map[consumer_id].add(key)

        declared_topics = self._config.topics
        if declared_topics != discovered_topics:
            raise InvalidTopologyException(f'Not all topics are declared: {discovered_topics - declared_topics}')

        log.info(f'Listeners: {self._config.consumers}')

        self._rabbit_client.declare_dead_letter()

        for topic in declared_topics:
            exchange_name = self._topic_to_exchange_map[topic]
            self._rabbit_client.declare_exchange(exchange_name)

        for consumer_id in self._config.consumers.keys():
            consumer_queue = get_consumer_queue(consumer_id)
            self._consumer_id_to_queue[consumer_id] = consumer_queue
            queue_result = self._rabbit_client.declare_queue(consumer_queue)
            consumer_listen_topics = self._consumer_to_events_map[consumer_id]
            for exchange, routing_key in consumer_listen_topics:
                self._rabbit_client.queue_bind(exchange, queue_result, routing_key)

    def get_exchange_key(self, topic: str) -> str:
        return self._topic_to_exchange_map[topic]

    def get_consumer_queue(self, process_id):
        return self._consumer_id_to_queue[process_id]
