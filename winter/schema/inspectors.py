import typing

from drf_yasg.inspectors import SwaggerAutoSchema as SwaggerAutoSchemaBase

from winter.routing import Route
from winter.routing import get_function_route


class SwaggerAutoSchema(SwaggerAutoSchemaBase):

    def get_consumes(self):
        route = self._get_route()
        if route is None:
            return []
        return [str(produce) for produce in route.consumes]

    def get_produces(self):
        route = self._get_route()
        if route is None:
            return []
        return [str(produce) for produce in route.produces]

    def _get_route(self) -> typing.Optional[Route]:
        controller_cls = type(self.view)
        func = getattr(controller_cls, self.method.lower(), None)
        controller_method = func.controller_method if func is not None else None
        if controller_method is None:
            return None
        return get_function_route(controller_method.func)
