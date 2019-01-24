from typing import List

from drf_yasg import openapi

from ..controller import ControllerMethod


class ControllerMethodInspector:
    def inspect_parameters(self, controller_method: ControllerMethod) -> List[openapi.Parameter]:
        return []


_method_inspectors: List[ControllerMethodInspector] = []


def register_controller_method_inspector(inspector: ControllerMethodInspector):
    _method_inspectors.append(inspector)


def get_controller_method_inspectors() -> List[ControllerMethodInspector]:
    return _method_inspectors
