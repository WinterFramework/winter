import abc
from typing import List

from openapi_schema_pydantic import Parameter

from winter.web.routing import Route


class RouteParametersInspector(abc.ABC):

    @abc.abstractmethod
    def inspect_parameters(self, route: 'Route') -> List[Parameter]:  # pragma: no cover
        return []


_route_parameters_inspectors: List[RouteParametersInspector] = []


def register_route_parameters_inspector(inspector: RouteParametersInspector):
    _route_parameters_inspectors.append(inspector)


def get_route_parameters_inspectors() -> List[RouteParametersInspector]:
    return _route_parameters_inspectors
