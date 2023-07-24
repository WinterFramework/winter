import argparse
import sys


from winter.core import get_injector
from .consumer import ConsumerWorker
from .setup import setup


class Parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def parse_args(parser_object):
    parser_object.add_argument(
        'consumer',
        type=str,
        help='Consumer ID',
    )
    return parser_object.parse_args()


if __name__ == '__main__':
    parser = Parser(description='Run consumer worker')
    args = parse_args(parser)
    consumer_id = args.consumer

    setup()

    injector = get_injector()
    worker = injector.get(ConsumerWorker)
    worker.start(consumer_id=consumer_id)
