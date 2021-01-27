from rest_framework.request import Request

import winter
from winter.core import ComponentMethod
from winter.web import Configurer
from winter.web import Interceptor
from winter.web import InterceptorRegistry
from winter.web import ResponseHeader


class HelloWorldInterceptor(Interceptor):
    @winter.response_header('x-hello-world', 'hello_world_header')
    @winter.response_header('x-method', 'method_header')
    def pre_handle(
        self,
        method: ComponentMethod,
        request: Request,
        method_header: ResponseHeader[str],
        hello_world_header: ResponseHeader[str],
    ):
        method_header.set(method.full_name)
        if 'hello_world' in request.query_params:
            hello_world_header.set('Hello, World!')


class HelloWorldConfigurer(Configurer):
    def add_interceptors(self, registry: InterceptorRegistry):
        registry.add_interceptor(HelloWorldInterceptor())
