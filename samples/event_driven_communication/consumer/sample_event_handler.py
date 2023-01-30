from tests.winter_messaging_outbox_transaction.test_event_publisher import SampleIntegrationEvent
from winter.messaging import event_handler


class MarkAsDoneEventHandler:
    @event_handler
    def on_marked_as_done(self, event: SampleIntegrationEvent):
        print('Handler handle: MarkedAsDoneIntegrationEvent')
        print(event)
