
from .producer.publish_processor import PublishProcessor
from winter.core import get_injector
from .setup import setup

if __name__ == '__main__':
    setup()

    injector = get_injector()
    processor = injector.get(PublishProcessor)
    processor.run()
