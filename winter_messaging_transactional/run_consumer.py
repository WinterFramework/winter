import argparse
import logging
import sys

import django

from winter.core import get_injector
from .consumer import ConsumerWorker
from .setup import setup

logger = logging.getLogger(__name__)


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
    parser_object.add_argument(
        '-p',
        '--package-module',
        type=str,
        dest='package_module',
        help='',
    )
    return parser_object.parse_args()


if __name__ == '__main__':
    parser = Parser(description='Run consumer worker')
    args = parse_args(parser)
    consumer_id = args.consumer
    package_name = args.package_module

    django.setup()
    setup()

    injector = get_injector()
    worker = injector.get(ConsumerWorker)
    logger.info(f'Starting message consumer id: %s; in package: %s', consumer_id, package_name)
    worker.start(consumer_id=consumer_id)
