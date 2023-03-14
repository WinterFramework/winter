import time

from tests.winter_messaging.app_sample.producer import SampleProducerNotifyEvent
from winter.messaging import event_handler


class ConsumerSlowEventHandler:

    @event_handler
    def on_notify_event_run_slow_operation(self, event: SampleProducerNotifyEvent):
        print('ConsumerSlowEventHandler handle: ', event)
        time.sleep(20)
