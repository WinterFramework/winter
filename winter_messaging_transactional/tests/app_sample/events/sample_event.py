from dataclasses import dataclass

from winter.messaging import Event
from winter.messaging import topic


@topic('sample-topic')
@dataclass(frozen=True)
class SampleEvent(Event):
    id: int
    payload: str
    can_be_handled_on_retry: bool = False
