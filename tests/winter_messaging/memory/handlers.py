from winter.core import annotate
from winter.messaging import event_handler
from .events import Event1
from .events import Event3


class OtherAnnotation:
    pass


other_annotation = annotate(OtherAnnotation, single=True)


class EventHandlers:
    def __init__(self):
        self.result = {'handlers': [], 'x': 0}

    @event_handler
    def handler1(self, event: Event1):
        self.result['handlers'].append(1)
        self.result['x'] += event.x

    @event_handler
    def handler2(self, event: Event1):
        self.result['handlers'].append(2)
        self.result['x'] += event.x

    @event_handler
    def handler3(self, event: Event3):
        self.result['handlers'].append(3)
        self.result['x'] += event.x

    @other_annotation
    def handler4(self, event: Event3):  # pragma: no cover
        self.result['handlers'].append(4)
        self.result['x'] += event.x
