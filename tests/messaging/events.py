from dataclasses import dataclass

from winter.messaging import Event


@dataclass
class Event1(Event):
    x: int


@dataclass
class Event2(Event):
    x: int


@dataclass
class Event3(Event):
    x: int
