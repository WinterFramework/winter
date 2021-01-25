from rest_framework.request import Request

import winter
from winter.web import Configurer
from winter.web import Interceptor
from winter.web import InterceptorRegistry
from winter.web import ResponseHeader


class HelloWorldInterceptor(Interceptor):
    @winter.response_header('x-hello-world', 'hello_world_header')
    def pre_handle(self, request: Request, hello_world_header: ResponseHeader[str]):
        if 'hello_world' in request.query_params:
            hello_world_header.set('Hello, World!')


class HelloWorldConfigurer(Configurer):
    def add_interceptors(self, registry: InterceptorRegistry):
        registry.add_interceptor(HelloWorldInterceptor())
