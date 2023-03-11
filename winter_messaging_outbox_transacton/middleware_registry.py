from typing import Callable
from typing import List


class Middleware(Callable):
    pass


class MiddlewareRegistry:
    def __init__(self):
        self._middlewares = []

    def set_middlewares(self, middlewares: List[Middleware]):
        self._middlewares = middlewares

    def run_with_middlewares(self, func: Callable[[None], None]):
        _next = func
        for middleware in reversed(self._middlewares):
            _next = middleware(_next)

        return _next
