from typing import List

from winter.core import Component
from winter.core.module_discovery import get_all_classes
from winter.core.module_discovery import import_recursively
from winter.web.routing import Route
from winter.web.routing import get_route


def get_routes_by_package(package_name: str) -> List[Route]:
    import_recursively(package_name)
    routes = []

    for class_name, cls in get_all_classes(package_name):
        component = Component.get_by_cls(cls)

        for method in component.methods:
            route = get_route(method)

            if route is not None:
                routes.append(route)

    return routes
