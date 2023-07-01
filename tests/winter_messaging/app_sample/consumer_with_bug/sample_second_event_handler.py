from tests.winter_messaging.app_sample.producer import SampleProducerNotifyEvent
from winter.messaging import event_handler


class ConsumerWithBugEventHandler:

    @event_handler
    def on_notify_event_raise_error(self, event: SampleProducerNotifyEvent):
        print('ConsumerSecondEventHandler handle: ', event)
        raise Exception('ConsumerSecondEventHandler handle: ', event)
