import abc
import typing

from rest_framework.request import Request as DRFRequest


class IOutputProcessor(abc.ABC):
    """Process controller method returned value so that it can be put to HttpResponse body.
    Common usage is to serializer some DTO to dict."""

    @abc.abstractmethod
    def process_output(self, output, request: DRFRequest):
        return output


class IOutputProcessorResolver(abc.ABC):
    """
    Resolves IOutputProcessor for a given body type.
    Due to python dynamic typing it's called after every controller method call.
    """

    @abc.abstractmethod
    def is_supported(self, body: typing.Any) -> bool:
        return False

    @abc.abstractmethod
    def get_processor(self, body: typing.Any) -> IOutputProcessor:
        pass


_registered_output_processors = {}
_registered_resolvers: typing.List[IOutputProcessorResolver] = []


def register_output_processor(func: typing.Callable, output_processor: IOutputProcessor):
    if func in _registered_output_processors:
        raise Exception(f'{func} already has registered output processor')
    _registered_output_processors[func] = output_processor


def register_output_processor_resolver(output_processor_resolver: IOutputProcessorResolver):
    _registered_resolvers.append(output_processor_resolver)


def get_output_processor(func, body: typing.Any) -> typing.Optional[IOutputProcessor]:
    output_processor = _registered_output_processors.get(func)
    if output_processor is not None:
        return output_processor
    for resolver in _registered_resolvers:
        if resolver.is_supported(body):
            return resolver.get_processor(body)
    return None
