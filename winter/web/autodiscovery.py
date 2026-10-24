from typing import List

from winter.application import Application
from winter.components import Component
from .routing import Route
from .routing import get_route


def find_routes(app: Application) -> List[Route]:
    """Routes of the API classes among the definitions of an application."""
    components = Component.get_all()
    return [
        route
        for definition in app.definitions
        if definition in components
        for method in components[definition].methods
        if (route := get_route(method)) is not None
    ]
