from dataclasses import dataclass
from typing import Callable
from typing import Mapping
from typing import Set

from injector import inject
from pika.adapters.blocking_connection import BlockingChannel
from pika.exchange_type import ExchangeType

from winter.messaging import EventHandlerRegistry
from winter.messaging import get_event_topic
from winter_messaging_outbox_transacton.utils import get_consumer_queue
from winter_messaging_outbox_transacton.utils import get_exchange_name
from winter_messaging_outbox_transacton.utils import get_routing_key


@dataclass
class TopologyConfig:
    topic_to_exchange_map: Mapping[str, str]

    def get_exchange_key(self, topic: str) -> str:
        return self.topic_to_exchange_map[topic]


class TopologyConfigurator:
    @inject
    def __init__(
        self,
        channel: BlockingChannel,
        handler_registry: EventHandlerRegistry,
    ) -> None:
        self._channel = channel
        self._handler_registry = handler_registry

    def autodiscover(self, package_name: str):
        self._handler_registry.autodiscover(package_name)

    def configure_topics(self):
        event_types = self._handler_registry.get_all_event_types()
        topics = self._collect_unique_topics(event_types)
        topic_to_exchange_map = {}
        for topic in topics:
            exchange_name = get_exchange_name(topic)
            self._channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=ExchangeType.topic.value,
                durable=True,
            )
            topic_to_exchange_map[topic] = exchange_name

        self._channel.confirm_delivery()
        return TopologyConfig(topic_to_exchange_map=topic_to_exchange_map)

    def configure_listener(self, consumer_id: str, config: TopologyConfig, on_message_callback: Callable):
        listeners = []
        handlers = self._handler_registry.get_all_handlers()

        merge_handlers_by_routing_keys = set()
        for handler_info in handlers:
            event_type = handler_info.arguments[0].type_
            topic_info = get_event_topic(event_type)
            event_type_name = event_type.__name__
            event_routing_key = get_routing_key(topic_info.name, event_type_name)
            routing_key = event_routing_key[:-len(event_type_name)] + '*'
            key = (topic_info.name, routing_key)
            merge_handlers_by_routing_keys.add(key)

        for topic, routing_key in merge_handlers_by_routing_keys:
            item = (topic, routing_key)
            listeners.append(item)
        print(f'Collected listeners: {listeners}')

        for topic, routing_key in listeners:
            exchange = config.get_exchange_key(topic)
            consumer = get_consumer_queue(consumer_id)
            result = self._channel.queue_declare(consumer, durable=True)
            self._channel.queue_bind(
                exchange=exchange,
                queue=result.method.queue,
                routing_key=routing_key,
            )
            self._channel.basic_consume(consumer, on_message_callback)

    @staticmethod
    def _collect_unique_topics(event_types) -> Set[str]:
        topics = set()
        for event_type in event_types:
            topic_info = get_event_topic(event_type)
            topics.add(topic_info.name)
        return topics
