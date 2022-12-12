from typing import Optional

from rest_framework.request import Request

from winter.core import ComponentMethod
from winter_django import HttpRequestArgumentResolver


def test_supports_optional_request():
    class Controller:
        def method(self, request: Optional[Request]):
            pass

    component_method = ComponentMethod.get_or_create(Controller.method)
    resolver = HttpRequestArgumentResolver()

    assert resolver.is_supported(component_method.arguments[0])
