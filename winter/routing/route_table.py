from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Type

from .route import Route
from .routing import get_route_annotation
from ..controller import ControllerMethod


class UnexpectedHttpMethod(Exception):
    def __init__(self, http_method: str):
        super().__init__(f'Using HTTP methods is not allowed at controller level: {http_method}')


class DuplicateRouteException(Exception):
    def __init__(self, route: Route):
        super().__init__(f'Duplicate route: {route}')


class RouteTable:
    def __init__(self):
        super().__init__()
        self._routes: List[Route] = []
        self._routes_set: Set[Route] = set()
        self._controller_method_routes: Dict[ControllerMethod, Route] = {}

    def add_route(self, route: Route):
        if route in self._routes_set:
            raise DuplicateRouteException(route)
        self._routes_set.add(route)
        self._routes.append(route)
        self._controller_method_routes[route.controller_method] = route

    def add_controller(self, controller_class: Type):
        for route in self._build_controller_routes(controller_class):
            self.add_route(route)

    def _build_controller_routes(self, controller_class: Type) -> List[Route]:
        from ..controller import get_controller_component
        routes = []
        controller_component = get_controller_component(controller_class)
        controller_route_annotation = get_route_annotation(controller_class)
        for controller_method in controller_component.methods:
            route_annotation = get_route_annotation(controller_method.func)
            url_path = route_annotation.url_path
            if controller_route_annotation is not None:
                if controller_route_annotation.http_method is not None:
                    raise UnexpectedHttpMethod(controller_route_annotation.http_method)
                url_path = controller_route_annotation.url_path + url_path
            routes.append(Route(
                route_annotation.http_method,
                url_path,
                controller_class,
                controller_method,
                route_annotation.produces,
                route_annotation.consumes,
            ))
        return routes

    def get_method_route(self, controller_method: ControllerMethod) -> Optional[Route]:
        return self._controller_method_routes.get(controller_method)

    def get_routes(self) -> List[Route]:
        return self._routes


route_table = RouteTable()
