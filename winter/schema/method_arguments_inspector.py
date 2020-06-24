import abc
from typing import List
from typing import TYPE_CHECKING

from drf_yasg import openapi

if TYPE_CHECKING:
    from winter.web.routing import Route


class MethodArgumentsInspector(abc.ABC):

    @abc.abstractmethod
    def inspect_parameters(self, route: 'Route') -> List[openapi.Parameter]:  # pragma: no cover
        return []


_method_inspectors: List[MethodArgumentsInspector] = []


def register_controller_method_inspector(inspector: MethodArgumentsInspector):
    _method_inspectors.append(inspector)


def get_method_arguments_inspectors() -> List[MethodArgumentsInspector]:
    return _method_inspectors
