from typing import Dict, TYPE_CHECKING, List, Tuple, Type

from .routing import Route

if TYPE_CHECKING:
    from ..controller import ControllerMethod


class DuplicateRouteException(Exception):
    def __init__(self, route: Route):
        super().__init__(f'Duplicate route: {route}')


class RouteTable:
    def __init__(self):
        super().__init__()
        self._routes: List[Tuple[Route, Type, 'ControllerMethod']] = []

    def add_route(self, route: Route, controller_class: Type, controller_method: 'ControllerMethod'):
        self._routes.append((route, controller_class, controller_method))

    def get_routes(self) -> Dict[Route, 'ControllerMethod']:
        routes = {}
        for route, controller_class, controller_method in self._routes:
            http_method = controller_method.http_method
            url_path = controller_method.url_path
            full_route = Route(url_path, http_method)
            if full_route in routes:
                raise DuplicateRouteException(full_route)
            routes[full_route] = controller_method
        return routes


route_table = RouteTable()
