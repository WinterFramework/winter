from pika import BlockingConnection
from pika import ConnectionParameters
from pika import URLParameters


def connect_to_rabbit():
    url = 'amqp://admin:mypass@localhost:5673/'
    params = URLParameters(url)
    # params = ConnectionParameters(heartbeat=600, blocked_connection_timeout=300)
    connection = BlockingConnection(params)
    return connection.channel()
