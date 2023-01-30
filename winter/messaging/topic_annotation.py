from dataclasses import dataclass
from typing import Type

from winter.core import annotate
from .event import Event
from ..core import Component


@dataclass(frozen=True)
class TopicAnnotation:
    name: str
    event_name: str


def topic(name: str, event_name: str = ''):
    return annotate(TopicAnnotation(name, event_name), single=True)


def get_event_topic(event_type: Type[Event]) -> TopicAnnotation:
    event_component = Component.get_by_cls(event_type)
    topic_info = event_component.annotations.get_one(TopicAnnotation)
    return topic_info
