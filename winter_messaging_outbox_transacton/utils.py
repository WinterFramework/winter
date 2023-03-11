def get_exchange_name(topic: str) -> str:
    return f'{topic}_events_topic'


def get_consumer_queue(consumer_id: str) -> str:
    return f'{consumer_id}_events_queue'


def get_routing_key(topic: str, message_type: str) -> str:
    return f'{topic}.{message_type}'