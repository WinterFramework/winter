import os
from urllib.parse import urlparse

from pika import BlockingConnection
from pika import ConnectionParameters
from pika import PlainCredentials

rabbit_url_var_key = 'WINTER_RABBIT_URL'


def create_connection():
    rabbit_url = os.getenv(rabbit_url_var_key)
    if not rabbit_url:
        raise ValueError(f'{rabbit_url_var_key} is not set')

    parsed_url = urlparse(rabbit_url)
    params = ConnectionParameters(
        host=parsed_url.hostname,
        port=parsed_url.port,
        credentials=PlainCredentials(parsed_url.username, parsed_url.password),
        heartbeat=int(os.getenv('WINTER_RABBIT_HEARTBEAT', 600)),
        blocked_connection_timeout=int(os.getenv('WINTER_RABBIT_TIMEOUT', 300)),
    )
    return BlockingConnection(params)
