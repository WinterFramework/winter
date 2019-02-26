import abc
import typing

import dataclasses
from rest_framework.request import Request as DRFRequest

from .core import ComponentMethod
from .core import annotate


class IOutputProcessor(abc.ABC):
    """Process controller method returned value so that it can be put to HttpResponse body.
    Common usage is to serializer some DTO to dict."""

    @abc.abstractmethod
    def process_output(self, output, request: DRFRequest):  # pragma: no cover
        return output


@dataclasses.dataclass
class OutputProcessorAnnotation:
    output_processor: IOutputProcessor


class IOutputProcessorResolver(abc.ABC):
    """
    Resolves IOutputProcessor for a given body type.
    Due to python dynamic typing it's called after every controller method call.
    """

    @abc.abstractmethod
    def is_supported(self, body: typing.Any) -> bool:  # pragma: no cover
        return False

    @abc.abstractmethod
    def get_processor(self, body: typing.Any) -> IOutputProcessor:  # pragma: no cover
        pass


_registered_resolvers: typing.List[IOutputProcessorResolver] = []


def register_output_processor(method: typing.Callable, output_processor: IOutputProcessor):
    return annotate(OutputProcessorAnnotation(output_processor), single=True)(method)


def register_output_processor_resolver(output_processor_resolver: IOutputProcessorResolver):
    _registered_resolvers.append(output_processor_resolver)


def get_output_processor(method: ComponentMethod, body: typing.Any) -> typing.Optional[IOutputProcessor]:
    output_processor_annotation = method.annotations.get_one_or_none(OutputProcessorAnnotation)
    if output_processor_annotation is not None:
        return output_processor_annotation.output_processor
    for resolver in _registered_resolvers:
        if resolver.is_supported(body):
            return resolver.get_processor(body)
    return None
