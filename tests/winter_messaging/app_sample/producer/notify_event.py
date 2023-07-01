from dataclasses import dataclass

from winter.messaging import Event
from winter.messaging import topic


@topic('sample-producer-topic')
@dataclass(frozen=True)
class SampleProducerNotifyEvent(Event):
    id: int
    name: str
