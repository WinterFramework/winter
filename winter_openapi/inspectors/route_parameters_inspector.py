import abc
from typing import List

from openapi_schema_pydantic import Parameter

from winter.web.routing import Route
import logging

class RouteParametersInspector(abc.ABC):

    @abc.abstractmethod
    def inspect_parameters(self, route: 'Route') -> List[Parameter]:  # pragma: no cover
        return []


_route_parameters_inspectors: List[RouteParametersInspector] = []


def register_route_parameters_inspector(inspector: RouteParametersInspector):
    inspector_classes = [inspector.__class__ for inspector in get_route_parameters_inspectors()]

    if inspector.__class__ in inspector_classes:
        logging.warning(f'{inspector.__class__.__name__} already registered')

    _route_parameters_inspectors.append(inspector)


def get_route_parameters_inspectors() -> List[RouteParametersInspector]:
    return _route_parameters_inspectors
