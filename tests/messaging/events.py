from dataclasses import dataclass

from winter.messaging import Event


@dataclass(frozen=True)
class Event1(Event):
    x: int


@dataclass(frozen=True)
class Event2(Event):
    x: int


@dataclass(frozen=True)
class Event3(Event):
    x: int


@dataclass(frozen=True)
class Event4(Event):
    x: int
