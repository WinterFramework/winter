from typing import Any

import dataclasses
from rest_framework.request import Request

from .output_processor import IOutputProcessor
from .output_processor import IOutputProcessorResolver


class DataclassesOutputProcessorResolver(IOutputProcessorResolver):
    def is_supported(self, body: Any) -> bool:
        return dataclasses.is_dataclass(body)

    def get_processor(self, body: Any) -> IOutputProcessor:
        return DataclassesOutputProcessor()


class DataclassesOutputProcessor(IOutputProcessor):
    def process_output(self, output, request: Request):
        return dataclasses.asdict(output)
