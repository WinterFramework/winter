import typing

from drf_yasg.inspectors import SwaggerAutoSchema as SwaggerAutoSchemaBase

from ..routing import Route
from ..routing import get_route


class SwaggerAutoSchema(SwaggerAutoSchemaBase):

    def get_consumes(self):
        route = self._get_route()
        if route is None or route.consumes is None:
            return super().get_consumes()
        return [str(media_type) for media_type in route.consumes]

    def get_produces(self):
        route = self._get_route()
        if route is None or route.produces is None:
            return super().get_produces()
        return [str(media_type) for media_type in route.produces]

    def _get_route(self) -> typing.Optional[Route]:
        view_cls = type(self.view)
        func = getattr(view_cls, self.method.lower(), None)
        if func is None:
            return None

        method = getattr(func, 'method', None)

        if method is None:
            return None
        return get_route(method)
