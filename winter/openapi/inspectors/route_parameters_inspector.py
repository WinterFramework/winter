import abc
from typing import List
from typing import TYPE_CHECKING

from openapi_pydantic.v3.v3_0 import Parameter

from winter.web.routing import Route

if TYPE_CHECKING:
    from winter.openapi.generator import SchemaRegistry


class RouteParametersInspector(abc.ABC):  # pragma: no cover

    @abc.abstractmethod
    def inspect_parameters(self, route: 'Route', schema_registry: 'SchemaRegistry') -> List[Parameter]:
        return []
