from typing import Callable
from typing import List


SignalHandler = Callable[[], None]


class Signal:
    def __init__(self):
        self._handlers: List[SignalHandler] = []

    def connect(self, handler: SignalHandler):
        self._handlers.append(handler)

    def send(self):
        for handler in self._handlers:
            handler()
