import argparse
import os
import sys


from winter.core import get_injector
from winter_messaging_transactional.startup_teardown import process_start
from winter_messaging_transactional.startup_teardown import process_stop
from .consumer import ConsumerWorker
from .setup import setup

if os.getenv('USE_COVERAGE', 'false').lower() == 'true':
    # noinspection PyUnresolvedReferences
    import winter_messaging_transactional.tests.coverage  # noqa: F401, F403


class Parser(argparse.ArgumentParser):
    def error(self, message): # pragma: no cover
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
    process_start()
    parser = Parser(description='Run consumer worker')
    args = parse_args(parser)
    consumer_id = args.consumer

    try:
        setup()
        injector = get_injector()
        worker = injector.get(ConsumerWorker)
        worker.start(consumer_id=consumer_id)
    finally:
        process_stop()
