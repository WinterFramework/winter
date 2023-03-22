from typing import Callable
from typing import Iterable
from typing import Type


class Middleware:
    def __init__(self, _next: Callable[[], None]):
        self._next = _next

    def __call__(self):
        self._next()


MiddlewareClass = Type[Middleware]
MiddlewareCollection = Iterable[MiddlewareClass]


class MiddlewareRegistry:
    def __init__(self, middlewares: MiddlewareCollection):
        self._middlewares = middlewares

    def run_with_middlewares(self, func: Callable[[], None]):
        _next = func
        for middleware in reversed(self._middlewares):
            _next = middleware(_next)

        _next()
