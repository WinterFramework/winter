import abc
from typing import List

from drf_yasg import openapi

from ..core import ComponentMethod


class MethodArgumentsInspector(abc.ABC):

    @abc.abstractmethod
    def inspect_parameters(self, controller_method: ComponentMethod) -> List[openapi.Parameter]:  # pragma: no cover
        return []


_method_inspectors: List[MethodArgumentsInspector] = []


def register_controller_method_inspector(inspector: MethodArgumentsInspector):
    _method_inspectors.append(inspector)


def get_method_arguments_inspectors() -> List[MethodArgumentsInspector]:
    return _method_inspectors
