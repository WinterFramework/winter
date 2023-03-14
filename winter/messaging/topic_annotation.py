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
    def wrapper(event_type):
        assert issubclass(event_type, Event), f'Class "{event_type}" must be a subclass of Event'
        event_name_ = event_name or event_type.__name__
        annotation_decorator = annotate(TopicAnnotation(name, event_name_), single=True)
        return annotation_decorator(event_type)

    return wrapper


def get_event_topic(event_type: Type[Event]) -> TopicAnnotation:
    event_component = Component.get_by_cls(event_type)
    return event_component.annotations.get_one(TopicAnnotation)
