from typing import Optional
from typing import Set
from typing import TYPE_CHECKING
from typing import Tuple
from typing import Type

from .routing import Route
from .routing import get_function_route

if TYPE_CHECKING:
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
        self._routes: Set[Tuple[Route, Type, 'ControllerMethod']] = set()

    def add_controller(self, controller_class: Type):
        from ..controller import get_controller_component
        controller_component = get_controller_component(controller_class)
        root_route = get_function_route(controller_class)
        for controller_method in controller_component.methods:
            route = get_function_route(controller_method.func)
            url_path = route.url_path
            if root_route is not None:
                if root_route.http_method is not None:
                    raise UnexpectedHttpMethod(root_route.http_method)
                url_path = root_route.url_path + url_path
            full_route = Route(url_path, route.http_method)
            if full_route in self._routes:
                raise DuplicateRouteException(full_route)
            self._routes.add((full_route, controller_class, controller_method))

    def get_method_route(self, controller_method: 'ControllerMethod') -> Optional[Route]:
        for route, controller_class, _controller_method in self._routes:
            if _controller_method is controller_method:
                return route
        return None

    def get_routes(self) -> Set[Route]:
        return {route for route, _, _ in self._routes}


route_table = RouteTable()
