import abc
import typing

from drf_yasg import openapi

if typing.TYPE_CHECKING:
    from ..routing import Route


class MethodArgumentsInspector(abc.ABC):

    @abc.abstractmethod
    def inspect_parameters(self, route: 'Route') -> typing.List[openapi.Parameter]:  # pragma: no cover
        return []


_method_inspectors: typing.List[MethodArgumentsInspector] = []


def register_controller_method_inspector(inspector: MethodArgumentsInspector):
    _method_inspectors.append(inspector)


def get_method_arguments_inspectors() -> typing.List[MethodArgumentsInspector]:
    return _method_inspectors
