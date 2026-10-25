from typing import Any
from typing import Mapping

import injector

from .request import Request


class _RequestValues(dict):
    """The values of the request-scoped providers of one request. Bound only in the injector of that request."""


class RequestScope(injector.Scope):
    """
    One value per request. The value lives in the injector of the request and goes away with it, so a
    request-scoped type exists only while Winter handles a request.
    """

    def get(self, key: type, provider: injector.Provider) -> injector.Provider:
        return _RequestScopedProvider(key, provider)


request_scope = injector.ScopeDecorator(RequestScope)


class _RequestScopedProvider(injector.Provider):
    def __init__(self, key: type, provider: injector.Provider):
        self._key = key
        self._provider = provider

    def get(self, asking_injector: injector.Injector) -> Any:
        # The scope belongs to the injector that binds the provider; the values belong to the one asked
        if not is_bound(asking_injector, _RequestValues):
            raise LookupError(f'{self._key.__name__} is request-scoped: it exists only while Winter handles a request')
        values = asking_injector.get(_RequestValues)
        if self._key not in values:
            values[self._key] = self._provider.get(asking_injector)
        return values[self._key]


def create_request_injector(
    app_injector: injector.Injector,
    request: Request,
    request_values: Mapping[type, object],
) -> injector.Injector:
    """The injector of one request: a child of the application's injector that binds the request."""

    def configure(binder: injector.Binder):
        for type_, value in {Request: request, **request_values, _RequestValues: _RequestValues()}.items():
            binder.bind(type_, to=injector.InstanceProvider(value))

    return app_injector.create_child_injector([configure])


def is_bound(injector_: injector.Injector, type_: type) -> bool:
    """Whether the injector or one of its parents binds the type explicitly, not only can create it."""
    binder = injector_.binder
    while binder is not None:
        if binder.has_explicit_binding_for(type_):
            return True
        binder = binder.parent
    return False
