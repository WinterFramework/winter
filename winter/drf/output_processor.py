from typing import Dict
from typing import Type

from rest_framework.request import Request
from rest_framework.serializers import Serializer

from .body_with_context import BodyWithContext
from ..output_processor import IOutputProcessor


class DRFOutputProcessor(IOutputProcessor):
    def __init__(self, serializer_class: Type[Serializer], serializer_args: Dict):
        self._serializer_class = serializer_class
        self._serializer_args = serializer_args

    def process_output(self, output, request: Request):
        if isinstance(output, BodyWithContext):
            instance = output.body
            context = output.context
        elif isinstance(output, tuple):
            instance, context = output
        else:
            instance = output
            context = {}
        context.update(request=request)
        serializer = self._serializer_class(instance=instance, context=context, **self._serializer_args)
        return serializer.data
