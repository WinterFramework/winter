from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import List
from typing import Optional

from rest_framework.request import Request


class IOutputProcessor(metaclass=ABCMeta):
    """Process controller method returned value so that it can be put to HttpResponse body.
    Common usage is to serializer some DTO to dict."""
    @abstractmethod
    def process_output(self, output, request: Request):
        return output


class IOutputProcessorResolver(metaclass=ABCMeta):
    """
    Resolves IOutputProcessor for a given body type.
    Due to python dynamic typing it's called after every controller method call.
    """
    @abstractmethod
    def is_supported(self, body: Any) -> bool:
        return False

    @abstractmethod
    def get_processor(self, body: Any) -> IOutputProcessor:
        pass


_registered_output_processors = {}
_registered_resolvers: List[IOutputProcessorResolver] = []


def register_output_processor(func, output_processor: IOutputProcessor):
    if func in _registered_output_processors:
        raise Exception(f'{func} already has registered output processor')
    _registered_output_processors[func] = output_processor


def register_output_processor_resolver(output_processor_resolver: IOutputProcessorResolver):
    _registered_resolvers.append(output_processor_resolver)


def get_output_processor(func, body: Any) -> Optional[IOutputProcessor]:
    output_processor = _registered_output_processors.get(func)
    if output_processor:
        return output_processor
    for resolver in _registered_resolvers:
        if resolver.is_supported(body):
            return resolver.get_processor(body)
    return None
