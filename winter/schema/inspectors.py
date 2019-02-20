import typing

from drf_yasg.inspectors import SwaggerAutoSchema as SwaggerAutoSchemaBase

from ..routing import Route
from ..routing import get_route_annotation


class SwaggerAutoSchema(SwaggerAutoSchemaBase):

    def get_consumes(self):
        route = self._get_route_annotation()
        if route is None:
            return super().get_consumes()
        return [str(media_type) for media_type in route.consumes]

    def get_produces(self):
        route = self._get_route_annotation()
        if route is None:
            return super().get_consumes()
        return [str(media_type) for media_type in route.produces]

    def _get_route_annotation(self) -> typing.Optional[Route]:
        controller_cls = type(self.view)
        func = getattr(controller_cls, self.method.lower(), None)
        controller_method = func.controller_method if func is not None else None
        if controller_method is None:
            return None
        return get_route_annotation(controller_method.func)
