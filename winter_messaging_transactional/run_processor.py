import argparse
import logging
import signal
import sys
from threading import Event

import django

from winter.core import get_injector
from .producer.publish_processor import PublishProcessor
from .setup import setup


class Parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


if __name__ == '__main__':
    parser = Parser(description='Run processor')
    parser.add_argument('processor', type=str, help='Processor ID')
    args = parser.parse_args()
    processor_id = args.processor

    django.setup()
    setup()

    injector = get_injector()
    processor = injector.get(PublishProcessor)
    processor.run()